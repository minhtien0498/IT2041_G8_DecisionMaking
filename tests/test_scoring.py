from src.solution2 import scoring
from src.solution2.core import normalize_score
from src.solution2.requirement_parser import ParsedRequirements


def test_normalize_lower_better_bounds():
    assert normalize_score(0, 0, 100, "lower_better") == 1.0
    assert normalize_score(100, 0, 100, "lower_better") == 0.0
    assert normalize_score(150, 0, 100, "lower_better") == 0.0  # clamp


def test_normalize_higher_better_bounds():
    assert normalize_score(100, 0, 100, "higher_better") == 1.0
    assert normalize_score(0, 0, 100, "higher_better") == 0.0


def test_normalize_equal_range_is_zero():
    assert normalize_score(50, 50, 50, "higher_better") == 0.0


def test_combine_alpha_beta():
    assert scoring.combine(1.0, 0.0, 0.7, 0.3) == 0.7
    assert scoring.combine(0.0, 1.0, 0.7, 0.3) == 0.3
    assert scoring.combine(1.0, 1.0, 0.7, 0.3) == 1.0


def test_filter_hard_rejects_over_budget_and_few_bedrooms():
    props = [
        {"property_id": "A", "price_million_vnd": 9000, "bedrooms": 3},
        {"property_id": "B", "price_million_vnd": 5000, "bedrooms": 1},
        {"property_id": "C", "price_million_vnd": 5000, "bedrooms": 3},
    ]
    form = {"budget_max_million": 8000, "min_bedrooms": 2}
    candidates, rejected = scoring.filter_hard(props, form)
    ids = [c["property_id"] for c in candidates]
    assert ids == ["C"]
    assert len(rejected) == 2


def test_score_additional_group_normalization():
    parsed = ParsedRequirements(soft=[{
        "raw_phrase": "nhiều chợ", "amenity_name": "market", "agg": "count",
        "radius_m": 1000, "derived_attribute": "nearby_market_count_within_1000m",
        "direction": "higher_better", "weight": 1.0,
    }])
    items = [
        {"property": {"property_id": "A"},
         "dynamic_values": {"nearby_market_count_within_1000m": {"value": 4}}},
        {"property": {"property_id": "B"},
         "dynamic_values": {"nearby_market_count_within_1000m": {"value": 0}}},
    ]
    scoring.score_additional(items, parsed)
    assert items[0]["additional_score"] == 1.0  # nhiều chợ nhất
    assert items[1]["additional_score"] == 0.0


def test_post_filter_hard_count():
    parsed = ParsedRequirements(hard=[{
        "raw_phrase": "phải có chợ 1km", "amenity_name": "market", "agg": "count",
        "radius_m": 1000, "derived_attribute": "nearby_market_count_within_1000m",
        "direction": "higher_better", "weight": 1.0,
    }])
    items = [
        {"property": {"property_id": "A"},
         "dynamic_values": {"nearby_market_count_within_1000m": {"value": 2}}},
        {"property": {"property_id": "B"},
         "dynamic_values": {"nearby_market_count_within_1000m": {"value": 0}}},
    ]
    kept = scoring.post_filter(items, parsed)
    ids = [i["property"]["property_id"] for i in kept]
    assert ids == ["A"]
