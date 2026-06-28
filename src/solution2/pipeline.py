"""Điều phối pipeline Solution 2.

Form + Additional Request -> Requirement Parsing -> Rule-based Top 10
-> Enrichment -> Post-filter -> Re-scoring/Re-ranking -> Top 5 -> Explanation.
"""

from . import requirement_parser, scoring, enrichment, explanation


# Map base attribute -> reason tag khi normalized_score đủ cao
_BASE_TAG = {
    "price": "good_price",
    "price_per_m2": "low_price_per_m2",
    "distance_to_nearest_school_m": "near_school",
    "distance_to_nearest_park_m": "near_park",
    "distance_to_nearest_supermarket_m": "near_supermarket",
    "distance_to_nearest_boulevard_m": "near_boulevard",
    "area_m2": "spacious",
}


def _reason_tags(item):
    tags = []
    for attr, detail in item.get("base_attributes", {}).items():
        if detail["normalized_score"] >= 0.6 and attr in _BASE_TAG:
            tags.append(_BASE_TAG[attr])
    for attr, detail in item.get("dynamic_attributes", {}).items():
        if detail["normalized_score"] >= 0.6:
            tags.append(f"good_{detail['amenity_name']}")
    return tags


def run(form, free_text, properties, *, alpha=0.7, beta=0.3, top_k_buffer=10, top_k=5):
    """Chạy toàn bộ pipeline Solution 2, trả về InternalResult (dict)."""
    parsed = requirement_parser.parse(form, free_text)

    # Bước 3: lọc cứng + chấm điểm form -> Top 10
    candidates, rejected = scoring.filter_hard(properties, form)
    if not candidates:
        return {
            "parsed": parsed, "total_properties": len(properties),
            "after_filter": 0, "rejected_count": len(rejected),
            "top5": [], "explanation": "Không có BĐS nào qua bộ lọc cứng.",
            "alpha": alpha, "beta": beta, "status": "no_candidates",
        }

    base_scored = scoring.score_base(candidates, form)
    base_scored.sort(key=lambda x: x["base_score"], reverse=True)
    top10 = base_scored[:top_k_buffer]

    has_measurable = bool(parsed.soft or parsed.hard)

    # Bước 4 & 5: enrichment + post-filter + additional scoring
    if has_measurable:
        enrichment.enrich_top10(top10, parsed)
        top10 = scoring.post_filter(top10, parsed)
        scoring.score_additional(top10, parsed)
    else:
        for it in top10:
            it["additional_score"] = 0.0
            it["dynamic_attributes"] = {}
            it["hard_constraint_pass"] = True

    # alpha/beta hiệu dụng: không có soft req đo được thì final = base
    if parsed.soft:
        a_eff, b_eff = alpha, beta
    else:
        a_eff, b_eff = 1.0, 0.0

    for it in top10:
        it["final_score"] = scoring.combine(
            it["base_score"], it["additional_score"], a_eff, b_eff
        )

    # Bước 6: re-rank -> Top 5
    top10.sort(key=lambda x: x["final_score"], reverse=True)
    top5 = top10[:top_k]
    for it in top5:
        it["reason_tags"] = _reason_tags(it)

    expl = explanation.explain(top5, parsed, form)

    return {
        "parsed": parsed,
        "total_properties": len(properties),
        "after_filter": len(candidates),
        "rejected_count": len(rejected),
        "top5": top5,
        "explanation": expl,
        "alpha": a_eff,
        "beta": b_eff,
        "status": "ok",
    }
