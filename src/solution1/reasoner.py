"""LLM #1 "Reasoner": bounded tool-calling loop, cap cứng 5 turns.

Turn 1 (bắt buộc, tool_choice ép `sql_filter`): hard filter từ form.
Turn 2-4 (tùy chọn, tool_choice="auto"): enrichment (`fetch_nearby_custom` /
`get_distance_to_place`), CÓ THỂ gọi NHIỀU LẦN cho các loại tiện ích khác nhau khi
free_text nhắc nhiều tiện ích không có cột dữ liệu (vd vừa nhà thuốc vừa phòng gym),
hoặc xuất JSON sớm hơn nếu đã đủ thông tin.
Turn 5 (bắt buộc, tool_choice="none"): ép xuất JSON candidates, không cho gọi tool nữa.
"""

import json
import re

from . import schema, tools

MAX_TURNS = 5
# Số lần thử lại THÊM (ngoài MAX_TURNS) khi model trả lời cuối cùng nhưng KHÔNG parse
# được JSON hợp lệ. Quan sát thực tế: cùng 1 model/case có thể thành công hoặc thất bại
# format JSON giữa các lần gọi khác nhau (không deterministic) — retry ngắn giúp tăng độ
# tin cậy đáng kể mà không tốn quá nhiều quota.
MAX_JSON_RETRIES = 2

RUBRIC = """
Thang điểm total_score từ 0.0 đến 1.0:
- > 0.8: rất phù hợp mọi tiêu chí (hard constraint + hầu hết soft_preferences).
- 0.5 - 0.8: phù hợp nhưng có đánh đổi rõ ràng ở ít nhất 1 tiêu chí soft.
- < 0.5: chỉ vừa đạt hard constraint, yếu ở phần soft_preferences.

Công thức tham khảo (không bắt buộc tuân theo tuyệt đối, nhưng dùng làm kim chỉ nam):
điểm nên tỉ lệ thuận với weight của từng soft_preferences entry và mức độ giá trị thực
tế đáp ứng min/max/direction (lower_better: càng gần min càng tốt; higher_better: càng
gần max càng tốt).
""".strip()

FEW_SHOT = """
Ví dụ input rút gọn (KHÔNG liên quan dữ liệu thật, chỉ minh họa định dạng):
form: budget_max_million=6000, soft_preferences={"price": {"weight":0.5, "direction":
"lower_better", "min":2000, "max":6000}, "distance_to_nearest_market_m": {"weight":0.5,
"direction":"lower_better", "min":0, "max":1000}}
candidates trả về từ sql_filter: [{"property_id": "XX_101", "price_million_vnd": 3200}]

Ví dụ output JSON ĐÚNG định dạng (chỉ minh họa format, không neo điểm số cụ thể):
{
  "candidates": [
    {
      "property_id": "XX_101",
      "total_score": 0.78,
      "hard_constraint_pass": true,
      "reason_tags": ["good_price", "near_market"],
      "why_recommended": "Giá thấp hơn nhiều so với ngân sách tối đa và rất gần chợ.",
      "tradeoff": "Diện tích hơi nhỏ so với các lựa chọn khác."
    }
  ],
  "unsupported_requirements": []
}
""".strip()


def _system_prompt(form, free_text, required_conditions):
    schema_block = schema.schema_prompt_block()
    cond_lines = "\n".join(
        f"  - {c['column']} {c['op']} {c['value']}" for c in required_conditions
    )
    soft_prefs = (form or {}).get("soft_preferences", {})
    return f"""
Bạn là một AI tư vấn bất động sản. Bạn có quyền truy cập CSDL qua tool.

{schema_block}

QUY TRÌNH BẮT BUỘC (tối đa 5 lượt gọi):
1. Lượt 1: PHẢI gọi tool `sql_filter`. Các điều kiện BẮT BUỘC phải có (suy ra từ form) là:
{cond_lines if cond_lines else "  (không có hard constraint định lượng nào trong form)"}
   Có thể thêm điều kiện khác nếu free_text yêu cầu rõ một ràng buộc cứng khác.
2. Lượt 2-4 (tùy chọn, CÓ THỂ gọi NHIỀU LẦN — mỗi lượt 1 tiện ích/địa điểm khác nhau):
   Xét gọi 1 trong 2 tool enrichment sau, TÙY LOẠI NHU CẦU:
   a) `fetch_nearby_custom` — dùng khi free_text nhắc một LOẠI TIỆN ÍCH CHUNG (không
      cần tên riêng/địa chỉ cụ thể) mà KHÔNG có cột dữ liệu tương ứng, ví dụ: "nhà
      thuốc" (pharmacy), "phòng gym"/"phòng tập" (gym), "chợ" (market), "quán cà phê"
      (cafe), "trường mầm non" (kindergarten). Các tiện ích này KHÔNG có cột
      distance_to_nearest_* nên PHẢI gọi tool này mới có dữ liệu để chấm điểm — KHÔNG
      được bỏ qua yêu cầu này. Dùng radius_m mặc định 1000 trừ khi free_text nêu rõ
      bán kính khác. NẾU free_text nhắc NHIỀU loại tiện ích khác nhau không có cột dữ
      liệu (vd vừa nhà thuốc vừa phòng gym), hãy gọi tool này NHIỀU LẦN — mỗi lượt 1
      loại tiện ích — cho đến khi đủ dữ liệu cho TẤT CẢ các loại được nhắc tới.
   b) `get_distance_to_place` — CHỈ dùng khi free_text nhắc một ĐỊA ĐIỂM/ĐỊA CHỈ CỤ THỂ
      có tên riêng (vd "123 Nguyễn Oanh", "Chung cư Landmark 81", "chỗ làm ở công ty X").
   KHÔNG gọi tool nào (bỏ qua các lượt này, chuyển thẳng sang xuất JSON) NẾU free_text
   CHỈ nhắc các tiện ích ĐÃ có cột dữ liệu sẵn: trường học, công viên, bệnh viện, siêu
   thị, trục đường lớn (distance_to_nearest_school_m/park_m/hospital_m/supermarket_m/
   boulevard_m, near_*_count_1km) — dùng thẳng cột có sẵn, KHÔNG gọi lại tool cho các
   loại này. Khi đã đủ dữ liệu cần thiết, DỪNG gọi tool và chuyển sang xuất JSON ngay
   (không cần dùng hết cả 3 lượt nếu không cần thiết).
5. Lượt cuối: TRẢ VỀ JSON (không gọi tool) đúng định dạng:
   {{"candidates": [{{"property_id", "total_score", "hard_constraint_pass",
   "reason_tags": [...], "why_recommended", "tradeoff"}}, ...],
   "unsupported_requirements": [...]}}
   CHỈ được chọn property_id đã có trong kết quả trả về từ sql_filter, KHÔNG được bịa
   thêm property_id khác. Sắp xếp candidates giảm dần theo total_score. Tối đa 10 candidates.
   LƯU Ý: có thể suy nghĩ ngắn gọn trước khi trả lời, nhưng KHÔNG viết dài dòng diễn giải
   từng bước tính toán ra ngoài — hãy đi thẳng vào JSON kết quả cuối cùng để tránh bị cắt
   bớt do giới hạn độ dài phản hồi.

{RUBRIC}

soft_preferences người dùng cung cấp (dùng để cân nhắc khi chấm điểm, KHÔNG dùng để lọc
cứng): {json.dumps(soft_prefs, ensure_ascii=False)}

free_text nhu cầu người dùng: "{free_text}"

{FEW_SHOT}
""".strip()


def _extract_json(text):
    """Trích JSON object từ text trả về của LLM (fallback khi model lẫn text quanh JSON)."""
    if not text:
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
    return None


def run(form, free_text, conn, llm_client):
    """Chạy bounded tool-calling loop (cap cứng MAX_TURNS lượt gọi LLM).

    Trả về (candidates_json | None, trace, executor).
    """
    required_conditions = schema.build_hard_conditions(form)
    executor = tools.ToolExecutor(conn, required_conditions=required_conditions)

    messages = [
        {"role": "system", "content": _system_prompt(form, free_text, required_conditions)},
        {"role": "user", "content": f"Form: {json.dumps(form, ensure_ascii=False)}\nNhu cầu: {free_text}"},
    ]

    trace = []

    for turn in range(1, MAX_TURNS + 1):
        is_first_turn = turn == 1
        is_last_turn = turn == MAX_TURNS

        if is_first_turn:
            tool_choice = {"type": "function", "function": {"name": "sql_filter"}}
            tool_schemas = tools.TOOL_SCHEMAS
        elif is_last_turn:
            tool_choice = "none"
            # Một số model (vd Nemotron) không tuân thủ tool_choice="none" nếu vẫn thấy
            # `tools` trong request — chúng vẫn nhồi 1 tool call giả dạng text thô vào
            # content. Bỏ hẳn `tools` ở lượt cuối để chặn đường, buộc trả JSON thuần.
            tool_schemas = None
            messages.append({
                "role": "user",
                "content": (
                    "Đã hết lượt gọi tool. Không còn tool nào khả dụng nữa — hãy trả lời "
                    "NGAY bằng đúng JSON candidates đã yêu cầu ở trên, không đề cập tool."
                ),
            })
        else:
            tool_choice = None  # "auto" — model tự quyết định gọi tool hay xuất JSON
            tool_schemas = tools.TOOL_SCHEMAS

        response, model_used, key_label = llm_client.chat(
            messages, tools=tool_schemas, tool_choice=tool_choice, max_tokens=7000,
        )
        msg = response.choices[0].message
        turn_trace = {"turn": turn, "model": model_used, "key": key_label, "tool_calls": []}
        trace.append(turn_trace)

        if not msg.tool_calls:
            # Model xuất JSON (hoặc text) thay vì gọi tool -> kết thúc loop tại đây.
            parsed = _extract_json(msg.content)
            turn_trace["raw_content_preview"] = (msg.content or "")[:800]
            turn_trace["finish_reason"] = response.choices[0].finish_reason

            # Retry ngắn nếu KHÔNG parse được JSON (model lỗi format lần này, không phải
            # do hết turn budget) — không tính vào MAX_TURNS vì đây là sửa lỗi format,
            # không phải một bước suy luận/tool-calling mới.
            retry_count = 0
            while parsed is None and retry_count < MAX_JSON_RETRIES:
                retry_count += 1
                messages.append({"role": "assistant", "content": msg.content})
                messages.append({
                    "role": "user",
                    "content": (
                        "Câu trả lời trước KHÔNG đúng định dạng JSON yêu cầu. Hãy trả lời "
                        "LẠI, CHỈ bằng JSON hợp lệ đúng schema đã yêu cầu ở trên, không "
                        "kèm bất kỳ text nào khác trước/sau JSON."
                    ),
                })
                response, model_used, key_label = llm_client.chat(
                    messages, tools=None, tool_choice="none", max_tokens=7000,
                )
                msg = response.choices[0].message
                retry_trace = {
                    "turn": f"{turn}-json_retry{retry_count}", "model": model_used,
                    "key": key_label, "tool_calls": [],
                    "raw_content_preview": (msg.content or "")[:800],
                    "finish_reason": response.choices[0].finish_reason,
                }
                trace.append(retry_trace)
                parsed = _extract_json(msg.content)

            return parsed, trace, executor

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
                tool_result = executor.dispatch(tc.function.name, args)
            except Exception as e:  # noqa: BLE001 — lỗi tool không crash cả pipeline
                args = {}
                tool_result = {"error": str(e)}
            turn_trace["tool_calls"].append({"name": tc.function.name, "args": args})
            messages.append({
                "role": "tool", "tool_call_id": tc.id,
                "content": json.dumps(tool_result, ensure_ascii=False),
            })

    # Hết MAX_TURNS mà vẫn chưa có JSON (không nên xảy ra vì turn cuối tool_choice="none",
    # nhưng giữ fallback an toàn thay vì crash).
    return None, trace, executor
