"""Map InternalResult -> output contract chung của nhóm.

Field bắt buộc: case_id, solution_id, status, top5[{rank, property_id,
total_score, hard_constraint_pass, reason_tags}], explanation_summary,
unsupported_requirements, latency_ms.
Field mở rộng: top5[{base_score, additional_score, dynamic_attributes}].
"""

SOLUTION_ID = "solution_2"


def to_contract(case_id, internal, latency_ms):
    """Chuyển kết quả nội bộ sang object đúng schema chung."""
    top5 = []
    for rank, item in enumerate(internal.get("top5", []), 1):
        prop = item["property"]
        top5.append({
            "rank": rank,
            "property_id": prop.get("property_id"),
            "total_score": item.get("final_score", item.get("base_score", 0.0)),
            "hard_constraint_pass": bool(item.get("hard_constraint_pass", True)),
            "reason_tags": item.get("reason_tags", []),
            # ── field mở rộng ──
            "base_score": item.get("base_score", 0.0),
            "additional_score": item.get("additional_score", 0.0),
            "dynamic_attributes": item.get("dynamic_attributes", {}),
            "title": prop.get("title", ""),
            "price_billion_vnd": prop.get("price_billion_vnd"),
        })

    parsed = internal.get("parsed")
    unsupported = list(getattr(parsed, "unsupported", []) or [])

    return {
        "case_id": case_id,
        "solution_id": SOLUTION_ID,
        "status": internal.get("status", "ok"),
        "top5": top5,
        "explanation_summary": internal.get("explanation", ""),
        "unsupported_requirements": unsupported,
        "latency_ms": latency_ms,
        # ── field mở rộng ──
        # Hệ thống hiểu gì từ free-text. Cần cho UI/report vì `hard` chỉ dùng để
        # lọc ứng viên nên không xuất hiện trong `dynamic_attributes`, dẫn tới
        # ràng buộc cứng có tác dụng thật nhưng lại vô hình với người xem.
        "parsed_requirements": _parsed_summary(parsed),
    }


def _parsed_summary(parsed):
    """Tóm tắt kết quả parse free-text để hiển thị/đối chiếu."""
    if parsed is None:
        return {"hard": [], "soft": [], "duplicates": [], "unsupported": []}

    def brief(req):
        return {
            "raw_phrase": req["raw_phrase"],
            "amenity_name": req["amenity_name"],
            "derived_attribute": req["derived_attribute"],
            "agg": req["agg"],
            "radius_m": req["radius_m"],
            "direction": req["direction"],
        }

    return {
        "hard": [brief(r) for r in getattr(parsed, "hard", [])],
        "soft": [brief(r) for r in getattr(parsed, "soft", [])],
        "duplicates": list(getattr(parsed, "duplicates", []) or []),
        "unsupported": list(getattr(parsed, "unsupported", []) or []),
    }
