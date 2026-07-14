import pytest

from src.solution2 import requirement_parser as rp

# Form mẫu: có school/park/supermarket trong soft_preferences (để test dedup)
FORM = {
    "budget_max_million": 8000,
    "min_bedrooms": 3,
    "soft_preferences": {
        "price": {"weight": 0.3, "direction": "lower_better", "min": 3000, "max": 8000},
        "distance_to_nearest_school_m": {"weight": 0.3, "direction": "lower_better", "min": 0, "max": 2000},
        "distance_to_nearest_park_m": {"weight": 0.2, "direction": "lower_better", "min": 0, "max": 2000},
        "distance_to_nearest_supermarket_m": {"weight": 0.2, "direction": "lower_better", "min": 0, "max": 1500},
    },
}


def test_empty_free_text_returns_nothing():
    parsed = rp.parse(FORM, "")
    assert parsed.soft == [] and parsed.hard == [] and parsed.unsupported == []


def test_count_marker_maps_to_count_attribute():
    parsed = rp.parse(FORM, "Ưu tiên nhiều chợ xung quanh.")
    assert len(parsed.soft) == 1
    req = parsed.soft[0]
    assert req["amenity_name"] == "market"
    assert req["agg"] == "count"
    assert req["direction"] == "higher_better"
    assert req["derived_attribute"].startswith("nearby_market_count_within_")


def test_proximity_maps_to_nearest_distance():
    parsed = rp.parse(FORM, "Muốn gần nhà thuốc.")
    assert len(parsed.soft) == 1
    req = parsed.soft[0]
    assert req["amenity_name"] == "pharmacy"
    assert req["agg"] == "nearest_distance"
    assert req["direction"] == "lower_better"


def test_hard_marker_goes_to_hard():
    parsed = rp.parse(FORM, "Nhà phải có chợ trong vòng 1km.")
    assert len(parsed.hard) == 1
    assert parsed.hard[0]["amenity_name"] == "market"
    assert parsed.hard[0]["radius_m"] == 1000


def test_radius_parsing_km():
    parsed = rp.parse(FORM, "Ưu tiên nhiều quán cà phê trong vòng 2km.")
    assert parsed.soft[0]["radius_m"] == 2000


def test_dedup_with_form():
    parsed = rp.parse(FORM, "Muốn gần siêu thị.")
    assert parsed.soft == [] and parsed.hard == []
    assert len(parsed.duplicates) == 1
    assert parsed.duplicates[0]["form_field"] == "distance_to_nearest_supermarket_m"


def test_subjective_is_unsupported():
    parsed = rp.parse(FORM, "Muốn khu yên tĩnh, hàng xóm thân thiện.")
    assert parsed.soft == []
    assert len(parsed.unsupported) == 2


def test_amenity_with_subjective_keeps_measurable():
    # "gần công viên cho yên tĩnh" -> park (duplicate), không bị nuốt thành unsupported
    parsed = rp.parse(FORM, "Ưu tiên gần công viên cho yên tĩnh.")
    assert len(parsed.duplicates) == 1
    assert parsed.unsupported == []


def test_kindergarten_priority_over_school():
    parsed = rp.parse(FORM, "Ưu tiên gần trường mầm non.")
    assert parsed.soft[0]["amenity_name"] == "kindergarten"


# ── Free-text KHÔNG dấu (validation set dùng chung của nhóm dùng kiểu này) ──

def test_unaccented_text_is_parsed():
    parsed = rp.parse(FORM, "Nha phai co cho trong vong 1km, uu tien gan truong mam non.")
    assert [r["amenity_name"] for r in parsed.hard] == ["market"]
    assert parsed.hard[0]["radius_m"] == 1000
    assert [r["amenity_name"] for r in parsed.soft] == ["kindergarten"]


def test_unaccented_pharmacy_and_gym():
    parsed = rp.parse(FORM, "Uu tien gan nha thuoc va co phong gym xung quanh.")
    assert {r["amenity_name"] for r in parsed.soft} == {"pharmacy", "gym"}


@pytest.mark.parametrize("text", [
    "de cho thue lai",          # "cho thuê" != "chợ"
    "khong gian du cho 2 vo chong",  # "đủ chỗ" != "chợ"
    "truong mam non cho con",   # "cho con" != "chợ"
])
def test_unaccented_false_friends_not_market(text):
    """Bỏ dấu làm 'chợ'->'cho' trùng giới từ 'cho'/'chỗ' — không được nhận nhầm."""
    parsed = rp.parse(FORM, text)
    assert all(r["amenity_name"] != "market" for r in parsed.soft + parsed.hard)
