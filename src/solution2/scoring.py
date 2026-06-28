"""Chấm điểm: base (form) + additional (thuộc tính động) + kết hợp final.

Công thức min-max và base scoring đồng nhất với Solution 1 để so sánh công bằng.
"""

from .core import normalize_score


# ── Lọc cứng theo form ──
def filter_hard(properties, form):
    """Lọc theo ngân sách và số phòng ngủ tối thiểu."""
    budget = form.get("budget_max_million")
    min_bed = form.get("min_bedrooms")
    candidates, rejected = [], []
    for p in properties:
        reasons = []
        if budget is not None and p["price_million_vnd"] > budget:
            reasons.append(f"price {p['price_million_vnd']} > {budget}")
        if min_bed is not None and p.get("bedrooms", 0) < min_bed:
            reasons.append(f"bedrooms {p.get('bedrooms')} < {min_bed}")
        (rejected if reasons else candidates).append((p, reasons) if reasons else p)
    return candidates, rejected


def _attr_value(prop, attr):
    if attr == "price":
        return prop["price_million_vnd"]
    if attr == "price_per_m2":
        return prop.get("price_per_m2_million", 0) or 0
    return prop.get(attr, 0) or 0


# ── Chấm điểm form (base) ──
def score_base(candidates, form):
    """Trả về list item {property, base_score, base_attributes}."""
    prefs = form.get("soft_preferences", {}) or {}
    scored = []
    for p in candidates:
        attributes = {}
        total = 0.0
        for attr, pref in prefs.items():
            raw = _attr_value(p, attr)
            norm = normalize_score(raw, pref["min"], pref["max"], pref["direction"])
            contrib = norm * pref["weight"]
            total += contrib
            attributes[attr] = {
                "value": round(raw, 2),
                "normalized_score": round(norm, 3),
                "weight": pref["weight"],
                "contribution_score": round(contrib, 4),
                "direction": pref["direction"],
            }
        scored.append({
            "property": p,
            "base_score": round(total, 4),
            "base_attributes": attributes,
        })
    return scored


# ── Chấm điểm thuộc tính động (additional) ──
def score_additional(enriched_items, parsed):
    """Chuẩn hóa min-max trong nội bộ Top 10 rồi tính additional_score.

    Mutates each item: thêm 'additional_score' và 'dynamic_attributes'.
    """
    soft_attrs = [r["derived_attribute"] for r in parsed.soft]
    if not soft_attrs or not enriched_items:
        for item in enriched_items:
            item["additional_score"] = 0.0
            item["dynamic_attributes"] = {}
        return enriched_items

    # Khoảng min/max cho từng thuộc tính trong nhóm
    ranges = {}
    for attr in soft_attrs:
        vals = [it["dynamic_values"][attr]["value"] for it in enriched_items
                if attr in it.get("dynamic_values", {})]
        if vals:
            ranges[attr] = (min(vals), max(vals))

    # Trọng số chuẩn hóa về tổng = 1 trên các soft req
    total_w = sum(r["weight"] for r in parsed.soft) or 1.0

    for item in enriched_items:
        dyn_attrs = {}
        add_total = 0.0
        for req in parsed.soft:
            attr = req["derived_attribute"]
            dv = item.get("dynamic_values", {}).get(attr)
            if dv is None or attr not in ranges:
                continue
            vmin, vmax = ranges[attr]
            norm = normalize_score(dv["value"], vmin, vmax, req["direction"])
            w_norm = req["weight"] / total_w
            contrib = norm * w_norm
            add_total += contrib
            dyn_attrs[attr] = {
                "value": dv["value"],
                "unit": "place" if req["agg"] == "count" else "meter",
                "source": "map_api",
                "amenity_name": req["amenity_name"],
                "radius_m": req["radius_m"],
                "preference_type": req["direction"],
                "normalized_score": round(norm, 3),
                "weight_normalized": round(w_norm, 3),
                "contribution_score": round(contrib, 4),
            }
        item["additional_score"] = round(add_total, 4)
        item["dynamic_attributes"] = dyn_attrs
    return enriched_items


def combine(base_score, additional_score, alpha=0.7, beta=0.3):
    return round(alpha * base_score + beta * additional_score, 4)


# ── Post-filter theo hard constraint mới ──
def hard_req_pass(item, parsed):
    """True nếu item thỏa toàn bộ hard requirement mới sinh từ free-text."""
    for req in parsed.hard:
        dv = item.get("dynamic_values", {}).get(req["derived_attribute"])
        if dv is None:
            return False
        if req["agg"] == "count":
            if dv["value"] < 1:
                return False
        else:  # nearest_distance: phải nằm trong bán kính yêu cầu
            if dv["value"] > req["radius_m"]:
                return False
    return True


def post_filter(enriched_items, parsed):
    """Loại ứng viên vi phạm hard requirement mới.

    Nếu loại sạch thì giữ nguyên (để vẫn trả được kết quả) nhưng đánh dấu fail.
    """
    if not parsed.hard:
        for it in enriched_items:
            it["hard_constraint_pass"] = True
        return enriched_items

    passed, failed = [], []
    for it in enriched_items:
        ok = hard_req_pass(it, parsed)
        it["hard_constraint_pass"] = ok
        (passed if ok else failed).append(it)

    return passed if passed else enriched_items
