"""Tool-based enrichment cho Top 10.

Với MỖI BĐS, sinh CÙNG một tập thuộc tính động từ các requirement đo lường được
(soft + hard). Bất biến: thuộc tính tạo cho 1 ứng viên thì tạo cho toàn bộ Top 10.
"""

from .amenity_tools import geocode, search_amenities


def _unique_reqs(parsed):
    """Gộp soft + hard, loại trùng theo derived_attribute."""
    seen = {}
    for req in list(parsed.soft) + list(parsed.hard):
        seen.setdefault(req["derived_attribute"], req)
    return list(seen.values())


def enrich_top10(scored_top10, parsed):
    """Thêm `dynamic_values` cho từng item trong Top 10.

    scored_top10: list các dict có khóa 'property'.
    parsed: ParsedRequirements.
    """
    reqs = _unique_reqs(parsed)

    for item in scored_top10:
        prop = item["property"]
        lat, lon = geocode(prop)
        dynamic_values = {}

        for req in reqs:
            res = search_amenities(lat, lon, req["amenity_name"], req["radius_m"])
            if req["agg"] == "count":
                value = res["count"]
            else:
                # nếu không có tiện ích nào, coi như rất xa (radius * 2)
                value = res["nearest_distance_m"]
                if value is None:
                    value = req["radius_m"] * 2

            dynamic_values[req["derived_attribute"]] = {
                "value": value,
                "amenity_name": req["amenity_name"],
                "agg": req["agg"],
                "radius_m": req["radius_m"],
                "direction": req["direction"],
                "weight": req["weight"],
            }

        item["dynamic_values"] = dynamic_values

    return scored_top10
