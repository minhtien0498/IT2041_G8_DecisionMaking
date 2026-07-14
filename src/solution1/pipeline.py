"""Điều phối pipeline Solution 1: reasoner -> guardrail -> explainer -> output_contract.

Short-circuit `status="no_candidate"` nếu hard filter suy từ form (turn 1 bắt buộc của
`sql_filter`) rỗng ngay từ đầu — không gọi LLM nào để tiết kiệm quota, và tránh trường
hợp LLM tự bịa candidate khi không có gì để chọn.
Degrade graceful về `status="error"` khi LLM lỗi lặp lại (thay vì crash cả batch case).
"""

from . import explainer, guardrail, reasoner, schema
from .llm_client import OpenRouterLLMClient
from .tools import ToolExecutor


def run(form, free_text, conn, reasoning_client=None, explanation_client=None, top_k=5):
    """Chạy toàn bộ pipeline Solution 1 cho 1 case, trả về InternalResult (dict)."""
    required_conditions = schema.build_hard_conditions(form)

    # Short-circuit: kiểm tra hard filter trước khi gọi bất kỳ LLM nào.
    probe = ToolExecutor(conn, required_conditions=required_conditions)
    probe.sql_filter([])
    if not probe.candidates_by_id:
        return {
            "status": "no_candidate",
            "top5": [],
            "explanation": "Không có bất động sản nào thỏa điều kiện lọc cứng từ form.",
            "unsupported_requirements": [],
            "models_used": [],
        }

    reasoning_client = reasoning_client or OpenRouterLLMClient("reasoning")
    try:
        candidates_json, trace, executor = reasoner.run(form, free_text, conn, reasoning_client)
    except Exception as e:  # noqa: BLE001 — LLM #1 lỗi lặp lại (mọi model trong pool đều lỗi)
        return {
            "status": "error",
            "top5": [],
            "explanation": f"Lỗi khi chạy LLM reasoning: {e}",
            "unsupported_requirements": [],
            "models_used": [],
        }

    top5, unsupported = guardrail.apply(candidates_json, executor.candidates_by_id, top_k=top_k)
    models_used = [f"{t['model']}[{t.get('key', '?')}]" for t in trace]
    # Tóm tắt tool nào đã được LLM #1 gọi ở mỗi turn (debug: kiểm tra xem
    # fetch_nearby_custom/get_distance_to_place có được dùng để làm giàu dữ liệu
    # ngoài các cột có sẵn hay không).
    tool_calls_summary = [
        {"turn": t["turn"], "tools": [tc["name"] for tc in t["tool_calls"]]}
        for t in trace if t.get("tool_calls")
    ]

    explanation_client = explanation_client or OpenRouterLLMClient("explanation")
    explanation_text, expl_model, expl_key = explainer.explain(form, free_text, top5, explanation_client)
    if expl_model:
        models_used.append(f"{expl_model}[{expl_key or '?'}]")

    if not candidates_json:
        status = "error"
    elif not top5:
        status = "error"
    else:
        status = "ok"

    return {
        "status": status,
        "top5": top5,
        "explanation": explanation_text,
        "unsupported_requirements": unsupported,
        "models_used": models_used,
        "tool_calls_summary": tool_calls_summary,
    }
