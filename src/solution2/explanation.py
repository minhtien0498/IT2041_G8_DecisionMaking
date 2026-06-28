"""Sinh giải thích tiếng Việt theo template (deterministic).

Không tự thêm tiêu chí hay đổi thứ hạng — chỉ diễn giải kết quả inference engine.
Pluggable cho LLM thật.
"""

# Nhãn thân thiện cho reason_tags
TAG_LABEL = {
    "good_price": "giá tốt",
    "near_school": "gần trường",
    "near_park": "gần công viên",
    "near_supermarket": "gần siêu thị",
    "near_boulevard": "gần trục đường lớn",
    "spacious": "diện tích rộng",
    "low_price_per_m2": "giá/m² thấp",
}


def _amenity_vi(amenity):
    return {
        "market": "chợ", "cafe": "quán cà phê", "kindergarten": "trường mầm non",
        "pharmacy": "nhà thuốc", "gym": "phòng gym", "school": "trường học",
        "supermarket": "siêu thị", "park": "công viên", "hospital": "bệnh viện",
        "boulevard": "trục đường lớn",
    }.get(amenity, amenity)


def explain(top5, parsed, form):
    """Trả về chuỗi giải thích tóm tắt cho Top 5."""
    if not top5:
        return "Không có bất động sản nào thỏa điều kiện."

    lines = []
    top1 = top5[0]
    p1 = top1["property"]
    lines.append(
        f"Top 1 là {p1.get('property_id')} ({p1.get('title', '')[:50]}) "
        f"với final_score {top1['final_score']:.3f} "
        f"(base {top1['base_score']:.3f}, additional {top1['additional_score']:.3f})."
    )

    # Vai trò của nhu cầu bổ sung
    if parsed.soft:
        names = ", ".join(_amenity_vi(r["amenity_name"]) for r in parsed.soft)
        lines.append(
            f"Nhu cầu bổ sung ({names}) đã được đưa vào tính điểm và có thể "
            f"thay đổi thứ hạng so với khi chỉ dùng form."
        )
        # Chỉ ra BĐS hưởng lợi nhất từ nhu cầu bổ sung
        best_add = max(top5, key=lambda x: x["additional_score"])
        if best_add["additional_score"] > 0:
            lines.append(
                f"{best_add['property'].get('property_id')} phù hợp nhất với nhu cầu "
                f"bổ sung (additional_score {best_add['additional_score']:.3f})."
            )
    else:
        lines.append("Không có nhu cầu bổ sung đo lường được; xếp hạng dựa trên form.")

    # Nhu cầu trùng với form
    if parsed.duplicates:
        dups = ", ".join(d["raw_phrase"] for d in parsed.duplicates)
        lines.append(f"Một số nhu cầu đã có sẵn trong form nên được hợp nhất: {dups}.")

    # Nhu cầu chưa hỗ trợ
    if parsed.unsupported:
        us = "; ".join(parsed.unsupported)
        lines.append(f"Các nhu cầu chưa hỗ trợ đo lường (đã gắn cờ): {us}.")

    return " ".join(lines)
