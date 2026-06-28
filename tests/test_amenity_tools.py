from src.solution2 import amenity_tools as at


def test_unknown_amenity_returns_zero():
    res = at.search_amenities(10.84, 106.65, "casino", 1000)
    assert res["count"] == 0
    assert res["nearest_distance_m"] is None


def test_count_grows_with_radius():
    lat, lon = 10.8388, 106.6535  # gần trung tâm Gò Vấp
    small = at.search_amenities(lat, lon, "market", 500)["count"]
    big = at.search_amenities(lat, lon, "market", 5000)["count"]
    assert big >= small


def test_nearest_distance_is_nonnegative():
    res = at.search_amenities(10.8388, 106.6535, "cafe", 1000)
    assert res["nearest_distance_m"] is not None
    assert res["nearest_distance_m"] >= 0


def test_known_amenities_contains_extended_types():
    known = at.known_amenities()
    for a in ["market", "cafe", "kindergarten", "pharmacy", "gym"]:
        assert a in known
