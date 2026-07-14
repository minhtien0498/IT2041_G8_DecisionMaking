"""Map InternalResult -> output contract chung của nhóm (Solution 1).

Field bắt buộc: case_id, solution_id, status, top5[{rank, property_id,
total_score, hard_constraint_pass, reason_tags}], explanation_summary,
unsupported_requirements, latency_ms.
Field mở rộng: top5[{why_recommended, tradeoff, title, price_billion_vnd}],
models_used (debug: model nào phục vụ mỗi turn).
"""

SOLUTION_ID = "solution_1"


def to_contract(case_id, internal, latency_ms):
    """Chuyển kết quả nội bộ (từ pipeline.run) sang object đúng schema chung."""
    top5 = []
    for rank, item in enumerate(internal.get("top5", []), 1):
        prop = item.get("property", {}) or {}
        top5.append({
            "rank": rank,
            "property_id": item.get("property_id"),
            "total_score": item.get("total_score", 0.0),
            "hard_constraint_pass": bool(item.get("hard_constraint_pass", True)),
            "reason_tags": item.get("reason_tags", []),
            # ── field mở rộng ──
            "why_recommended": item.get("why_recommended", ""),
            "tradeoff": item.get("tradeoff", ""),
            "title": prop.get("title", ""),
            "price_billion_vnd": prop.get("price_billion_vnd"),
        })

    return {
        "case_id": case_id,
        "solution_id": SOLUTION_ID,
        "status": internal.get("status", "ok"),
        "top5": top5,
        "explanation_summary": internal.get("explanation", ""),
        "unsupported_requirements": internal.get("unsupported_requirements", []),
        "latency_ms": latency_ms,
        # ── field mở rộng (debug) ──
        "models_used": internal.get("models_used", []),
        "tool_calls_summary": internal.get("tool_calls_summary", []),
    }
