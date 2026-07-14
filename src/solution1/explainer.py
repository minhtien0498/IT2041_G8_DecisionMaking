"""LLM #2 "Explainer": single-shot, KHÔNG có tool access.

Sinh `explanation_summary` CHI TIẾT, rành mạch, mượt mà cho top5 đã guard — giải thích
tổng quan + lần lượt từng lựa chọn để người dùng hiểu tường tận vì sao được đề xuất.
Không ghi đè `why_recommended`/`tradeoff` của từng item (đã có từ LLM #1) — bài viết của
LLM #2 là lớp diễn giải tổng hợp, tự nhiên hơn, dựa trên đúng dữ liệu đã có.
Fallback template (không LLM) nếu lỗi/timeout.
"""

import json
import re

SYSTEM_PROMPT = (
    "Bạn là một chuyên gia tư vấn bất động sản giàu kinh nghiệm. Nhiệm vụ của bạn là "
    "viết đoạn giải thích RÀNH MẠCH, MƯỢT MÀ và RÕ RÀNG bằng tiếng Việt tự nhiên, giúp "
    "người dùng hiểu tường tận vì sao mỗi bất động sản được đề xuất và nên cân nhắc điều "
    "gì khi lựa chọn. Giải thích càng chi tiết càng tốt, nhưng luôn bám sát đúng dữ liệu "
    "được cung cấp, không suy diễn hay bịa thêm thông tin."
)


def _template_fallback(top5):
    if not top5:
        return "Không tìm thấy bất động sản phù hợp với yêu cầu đã cho."
    top1 = top5[0]
    tags = ", ".join(top1["reason_tags"]) if top1["reason_tags"] else "phù hợp ngân sách"
    return (
        f"Top 1 ({top1['property_id']}) nổi bật nhờ {tags}. "
        f"Danh sách gồm {len(top5)} lựa chọn được xếp hạng theo mức độ phù hợp tổng thể."
    )


def _looks_complete(text):
    """True nếu text kết thúc bằng dấu câu hợp lý (không bị cắt giữa chừng)."""
    return text.rstrip().endswith((".", "!", "?", ":", ")", '"', "”", "*", "】", "。"))


def _dedupe_repeated_text(text, marker_len=150):
    """Một số model (vd Nemotron) đôi khi KHÔNG dừng lại sau khi viết xong câu trả lời,
    mà lặp lại NGUYÊN VĂN toàn bộ nội dung lần thứ 2 — đôi khi còn "khởi động lại" giữa
    chừng TRƯỚC KHI viết xong bản đầu (khiến bản đầu bị cắt ngang), rồi mới viết trọn vẹn
    ở bản lặp lại thứ 2. Phát hiện bằng cách tìm đoạn mở đầu (marker_len ký tự đầu) có
    xuất hiện lại lần nữa hay không; nếu có, ưu tiên giữ lại bản nào kết thúc trọn vẹn
    (ưu tiên bản 2 nếu bản 1 bị cắt ngang), thay vì luôn cắt bỏ phần sau."""
    if not text or len(text) < marker_len * 2:
        return text
    marker = text[:marker_len].strip()
    if not marker:
        return text
    second_pos = text.find(marker, marker_len)
    if second_pos == -1:
        return text
    first_copy = text[:second_pos].rstrip()
    second_copy = text[second_pos:].rstrip()
    if _looks_complete(second_copy) and not _looks_complete(first_copy):
        return second_copy
    return first_copy


def _extract_explanation_text(content):
    """Ưu tiên text thuần (model không bắt buộc trả JSON). Nếu model vẫn lỡ bọc JSON
    dạng {"explanation_summary": "..."}, tự bóc tách cho gọn thay vì hiển thị JSON thô."""
    if not content:
        return None
    stripped = content.strip()
    if stripped.startswith("{"):
        try:
            data = json.loads(stripped)
            if isinstance(data, dict) and data.get("explanation_summary"):
                return _dedupe_repeated_text(data["explanation_summary"].strip())
        except json.JSONDecodeError:
            match = re.search(r'"explanation_summary"\s*:\s*"(.*)"\s*}\s*$', stripped, re.DOTALL)
            if match:
                return _dedupe_repeated_text(match.group(1).strip())
    return _dedupe_repeated_text(stripped)


def _build_prompt(form, free_text, top5):
    items = []
    for item in top5:
        prop = item["property"]
        items.append({
            "rank": item["rank"],
            "property_id": item["property_id"],
            "total_score": item["total_score"],
            "reason_tags": item["reason_tags"],
            "why_recommended": item["why_recommended"],
            "tradeoff": item["tradeoff"],
            "title": prop.get("title"),
            "price_million_vnd": prop.get("price_million_vnd"),
            "area_m2": prop.get("area_m2"),
            "bedrooms": prop.get("bedrooms"),
            "district": prop.get("district"),
            "ward": prop.get("ward"),
        })

    return f"""
Nhu cầu người dùng: "{free_text}"
Form: {json.dumps(form, ensure_ascii=False)}

Top {len(top5)} bất động sản đã được xếp hạng sẵn (KHÔNG đổi thứ tự, chỉ diễn giải):
{json.dumps(items, ensure_ascii=False, indent=2)}

Hãy viết một bài giải thích chi tiết theo cấu trúc sau:
1. TỔNG QUAN: vì sao Top 1 nổi bật nhất so với nhu cầu người dùng, so với các lựa chọn
   còn lại trong danh sách.
2. LẦN LƯỢT TỪNG LỰA CHỌN (không chỉ Top 1): với mỗi bất động sản trong danh sách, nêu rõ
   điểm mạnh, điểm còn hạn chế/đánh đổi so với nhu cầu người dùng.
3. SO SÁNH: nếu có đánh đổi rõ ràng giữa các lựa chọn (vd rẻ hơn nhưng xa tiện ích hơn,
   diện tích lớn hơn nhưng giá cao hơn), hãy nêu rõ để người dùng dễ dàng so sánh và ra
   quyết định.

Yêu cầu văn phong:
- Tiếng Việt tự nhiên, rành mạch, mượt mà, dễ đọc — có thể chia nhiều đoạn.
- Giải thích càng chi tiết, càng đầy đủ càng tốt, KHÔNG giới hạn số câu.
- TUYỆT ĐỐI KHÔNG bịa thêm thông tin ngoài dữ liệu đã cung cấp ở trên.
- Trả lời bằng văn bản thuần (không cần bọc JSON, không cần markdown code block).
""".strip()


def explain(form, free_text, top5, llm_client):
    """Sinh explanation_summary chi tiết. Trả về (text, model_used | None, key_label | None)."""
    if not top5:
        return _template_fallback(top5), None, None

    try:
        prompt = _build_prompt(form, free_text, top5)
        response, model_used, key_label = llm_client.chat(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=8000,
            temperature=0.4,
            frequency_penalty=0.4,
            presence_penalty=0.2,
        )
        content = response.choices[0].message.content
        text = _extract_explanation_text(content)
        if text:
            return text, model_used, key_label
    except Exception:  # noqa: BLE001 — không để lỗi LLM #2 làm crash cả pipeline
        pass

    return _template_fallback(top5), None, None

