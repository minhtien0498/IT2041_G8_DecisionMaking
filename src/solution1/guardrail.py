"""Guardrail thuần code (KHÔNG LLM): grounding filter + dedupe + sort + renumber + cắt top_k.

Chống hallucination: loại bỏ bất kỳ `property_id` nào KHÔNG nằm trong candidate set trả
về từ `sql_filter` (`executor.candidates_by_id`). Không backfill nếu top5 còn <5 phần tử
— hợp lệ theo output contract chung (`top5` được phép <5).
"""


def apply(candidates_json, candidates_by_id, top_k=5):
    """Chuẩn hóa JSON candidates từ LLM #1 thành top5 đã guard.

    `candidates_json`: dict trả về từ `reasoner.run` (có thể None nếu LLM lỗi/không
    parse được JSON). `candidates_by_id`: dict property_id -> row, lấy từ
    `executor.candidates_by_id` sau khi `sql_filter` đã chạy.

    Trả về (top5, unsupported_requirements).
    """
    if not candidates_json:
        return [], []

    raw_candidates = candidates_json.get("candidates", []) or []
    unsupported = candidates_json.get("unsupported_requirements", []) or []

    grounded = []
    seen_ids = set()
    for item in raw_candidates:
        if not isinstance(item, dict):
            continue
        pid = item.get("property_id")
        if pid is None or pid not in candidates_by_id:
            continue  # loại property_id hallucinated (không thuộc candidate set)
        if pid in seen_ids:
            continue  # dedupe
        seen_ids.add(pid)
        grounded.append({
            "property_id": pid,
            "total_score": item.get("total_score", 0.0) or 0.0,
            "hard_constraint_pass": bool(item.get("hard_constraint_pass", True)),
            "reason_tags": item.get("reason_tags", []) or [],
            "why_recommended": item.get("why_recommended", ""),
            "tradeoff": item.get("tradeoff", ""),
            "property": candidates_by_id[pid],
        })

    grounded.sort(key=lambda x: x["total_score"], reverse=True)
    top = grounded[:top_k]
    for rank, item in enumerate(top, 1):
        item["rank"] = rank

    return top, unsupported
