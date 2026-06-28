import json
import os

from src.solution2 import pipeline
from src.solution2.output_contract import to_contract

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROPS = json.load(open(os.path.join(ROOT, "data", "go_vap_enriched.json"), encoding="utf-8"))

FAMILY_FORM = {
    "budget_max_million": 8000,
    "min_bedrooms": 3,
    "soft_preferences": {
        "price": {"weight": 0.25, "direction": "lower_better", "min": 3000, "max": 8000},
        "distance_to_nearest_school_m": {"weight": 0.25, "direction": "lower_better", "min": 0, "max": 2000},
        "distance_to_nearest_park_m": {"weight": 0.20, "direction": "lower_better", "min": 0, "max": 2000},
        "distance_to_nearest_supermarket_m": {"weight": 0.15, "direction": "lower_better", "min": 0, "max": 1500},
        "area_m2": {"weight": 0.15, "direction": "higher_better", "min": 30, "max": 150},
    },
}

REQUIRED_TOP5_FIELDS = {"rank", "property_id", "total_score", "hard_constraint_pass", "reason_tags"}
REQUIRED_TOP_FIELDS = {"case_id", "solution_id", "status", "top5",
                       "explanation_summary", "unsupported_requirements", "latency_ms"}


def _run(free_text):
    internal = pipeline.run(FAMILY_FORM, free_text, PROPS)
    return to_contract("TEST", internal, 12.3)


def test_output_matches_contract_schema():
    out = _run("Ưu tiên nhiều chợ xung quanh.")
    assert REQUIRED_TOP_FIELDS.issubset(out.keys())
    assert out["solution_id"] == "solution_2"
    assert len(out["top5"]) <= 5
    for i, row in enumerate(out["top5"], 1):
        assert REQUIRED_TOP5_FIELDS.issubset(row.keys())
        assert row["rank"] == i  # rank tăng dần liên tục


def test_total_score_descending():
    out = _run("Ưu tiên nhiều chợ xung quanh.")
    scores = [r["total_score"] for r in out["top5"]]
    assert scores == sorted(scores, reverse=True)


def test_free_text_changes_ranking():
    # Free-text "nhiều chợ" phải làm Top 5 khác với khi chỉ dùng form
    base = [r["property_id"] for r in _run("")["top5"]]
    with_text = [r["property_id"] for r in _run("Ưu tiên nhiều chợ xung quanh.")["top5"]]
    assert base != with_text


def test_unsupported_flagged_in_contract():
    out = _run("Muốn khu yên tĩnh, hợp phong thủy.")
    assert len(out["unsupported_requirements"]) == 2


def test_empty_free_text_behaves_like_form():
    out = _run("")
    # Không có nhu cầu bổ sung -> additional_score = 0, final = base
    for row in out["top5"]:
        assert row["additional_score"] == 0.0
        assert row["total_score"] == row["base_score"]
