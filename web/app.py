"""FastAPI web app for interactive recommendation and validation."""

import json
import math
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.solution2 import pipeline as solution2_pipeline
from src.solution2.output_contract import to_contract as solution2_to_contract

try:
    from src.solution1 import db as solution1_db
    from src.solution1 import pipeline as solution1_pipeline
    from src.solution1.output_contract import to_contract as solution1_to_contract
except Exception:  # noqa: BLE001
    solution1_db = None
    solution1_pipeline = None
    solution1_to_contract = None


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
WEB_DIR = ROOT / "web"
PROPERTIES_FILE = DATA_DIR / "go_vap_tan_binh_100_enriched.json"
VALIDATION_V1_FILE = DATA_DIR / "validation_cases_v1.json"
VALIDATION_50_FILE = DATA_DIR / "validation_50_scenarios.json"

load_dotenv(ROOT / ".env")

app = FastAPI(title="IT2041 G8 Real Estate DSS")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

_properties_cache: list[dict[str, Any]] | None = None
_solution1_loaded = False


class RecommendationRequest(BaseModel):
    form: dict[str, Any]
    free_text: str = ""
    solution: str = Field(default="solution2", pattern="^(solution1|solution2|both)$")
    top_x: int = Field(default=5, ge=1, le=20)


class ValidationRequest(BaseModel):
    form: dict[str, Any]
    free_text: str = ""
    solution: str = Field(default="both", pattern="^(solution1|solution2|both)$")
    top_x: int = Field(default=5, ge=1, le=20)
    case_id: str | None = None
    expected: dict[str, Any] | None = None
    ground_truth_top5: list[str] | None = None
    manual_scores: dict[str, float] | None = None


class BatchValidationRequest(BaseModel):
    solution: str = Field(default="both", pattern="^(solution1|solution2|both)$")
    dataset: str = Field(default="validation_cases_v1", pattern="^(validation_cases_v1|validation_50_scenarios)$")
    limit: int = Field(default=5, ge=1, le=50)
    top_x: int = Field(default=5, ge=1, le=20)


def load_properties() -> list[dict[str, Any]]:
    global _properties_cache
    if _properties_cache is None:
        with open(PROPERTIES_FILE, encoding="utf-8") as file:
            _properties_cache = json.load(file)
    return _properties_cache


def load_json(path: Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def get_property_map() -> dict[str, dict[str, Any]]:
    return {prop["property_id"]: prop for prop in load_properties()}


def trim_top(contract: dict[str, Any], top_x: int) -> dict[str, Any]:
    contract = dict(contract)
    contract["top5"] = contract.get("top5", [])[:top_x]
    return contract


def run_solution2(form: dict[str, Any], free_text: str, top_x: int, case_id: str) -> dict[str, Any]:
    start = time.perf_counter()
    internal = solution2_pipeline.run(
        form,
        free_text,
        load_properties(),
        top_k_buffer=max(10, top_x),
        top_k=top_x,
    )
    latency_ms = round((time.perf_counter() - start) * 1000, 1)
    return trim_top(solution2_to_contract(case_id, internal, latency_ms), top_x)


def ensure_solution1_db() -> Any:
    global _solution1_loaded
    if solution1_db is None:
        raise RuntimeError("Không import được module Solution 1.")
    try:
        conn = solution1_db.get_connection()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            "Solution 1 chưa kết nối được Postgres. Hãy mở Docker Desktop rồi chạy "
            "`docker compose up -d solution1_db`."
        ) from exc
    if not _solution1_loaded:
        solution1_db.init_schema(conn)
        solution1_db.load_properties(conn, str(PROPERTIES_FILE))
        _solution1_loaded = True
    return conn


def run_solution1(form: dict[str, Any], free_text: str, top_x: int, case_id: str) -> dict[str, Any]:
    if not os.environ.get("OPENROUTER_API_KEYS") and not os.environ.get("OPENROUTER_API_KEY"):
        raise RuntimeError("Thiếu OPENROUTER_API_KEY(S), Solution 1 cần LLM qua OpenRouter.")
    if solution1_pipeline is None or solution1_to_contract is None:
        raise RuntimeError("Không import được pipeline Solution 1.")

    start = time.perf_counter()
    with ensure_solution1_db() as conn:
        internal = solution1_pipeline.run(form, free_text, conn, top_k=top_x)
    latency_ms = round((time.perf_counter() - start) * 1000, 1)
    return trim_top(solution1_to_contract(case_id, internal, latency_ms), top_x)


def solution_error(solution_id: str, error: Exception, case_id: str) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "solution_id": solution_id,
        "status": "error",
        "top5": [],
        "explanation_summary": str(error),
        "unsupported_requirements": [],
        "latency_ms": 0,
    }


def run_selected_solutions(form: dict[str, Any], free_text: str, solution: str, top_x: int, case_id: str) -> dict[str, Any]:
    selected = ["solution1", "solution2"] if solution == "both" else [solution]
    results = {}
    for item in selected:
        try:
            if item == "solution1":
                results["solution1"] = run_solution1(form, free_text, top_x, case_id)
            else:
                results["solution2"] = run_solution2(form, free_text, top_x, case_id)
        except Exception as exc:  # noqa: BLE001
            solution_id = "solution_1" if item == "solution1" else "solution_2"
            results[item] = solution_error(solution_id, exc, case_id)
    return results


def precision_at_k(recommended_ids: list[str], ground_truth_ids: list[str], k: int) -> float:
    return sum(1 for item in recommended_ids[:k] if item in ground_truth_ids) / k if k else 0.0


def recall_at_k(recommended_ids: list[str], ground_truth_ids: list[str], k: int) -> float:
    return sum(1 for item in recommended_ids[:k] if item in ground_truth_ids) / len(ground_truth_ids) if ground_truth_ids else 0.0


def ndcg_at_k(recommended_ids: list[str], ground_truth_ids: list[str], k: int) -> float:
    relevance = {item: len(ground_truth_ids) - index for index, item in enumerate(ground_truth_ids)}
    dcg = sum(relevance.get(item, 0) / math.log2(index + 2) for index, item in enumerate(recommended_ids[:k]))
    idcg = sum((len(ground_truth_ids) - index) / math.log2(index + 2) for index in range(min(k, len(ground_truth_ids))))
    return dcg / idcg if idcg else 0.0


def average_precision(recommended_ids: list[str], ground_truth_ids: list[str], k: int) -> float:
    hits = 0
    total = 0.0
    for index, item in enumerate(recommended_ids[:k]):
        if item in ground_truth_ids:
            hits += 1
            total += hits / (index + 1)
    return total / min(k, len(ground_truth_ids)) if ground_truth_ids else 0.0


def hard_constraint_score(contract: dict[str, Any], form: dict[str, Any]) -> dict[str, Any]:
    prop_map = get_property_map()
    top_items = contract.get("top5", [])
    violations = []
    for item in top_items:
        prop = prop_map.get(item.get("property_id"), {})
        reasons = []
        budget = form.get("budget_max_million")
        min_bedrooms = form.get("min_bedrooms")
        if budget is not None and prop.get("price_million_vnd", 0) > budget:
            reasons.append(f"price {prop.get('price_million_vnd')} > {budget}")
        if min_bedrooms is not None and prop.get("bedrooms", 0) < min_bedrooms:
            reasons.append(f"bedrooms {prop.get('bedrooms')} < {min_bedrooms}")
        if not item.get("hard_constraint_pass", True):
            reasons.append("pipeline marked hard_constraint_pass=false")
        if reasons:
            violations.append({"property_id": item.get("property_id"), "reasons": reasons})
    total = len(top_items)
    pass_rate = (total - len(violations)) / total if total else 1.0
    return {"pass_rate": round(pass_rate, 4), "violations": violations}


_PRIORITY_TAGS = {
    "near school": "near_school",
    "gần trường": "near_school",
    "near park": "near_park",
    "gần công viên": "near_park",
    "near supermarket": "near_supermarket",
    "gần siêu thị": "near_supermarket",
    "near hospital": "near_hospital",
    "near boulevard": "near_boulevard",
    "reasonable price": "good_price",
    "giá tốt": "good_price",
    "low price per m2": "low_price_per_m2",
    "spacious": "spacious",
    "diện tích": "spacious",
}


def expected_priority_score(contract: dict[str, Any], expected: dict[str, Any] | None) -> dict[str, Any]:
    priorities = (expected or {}).get("soft_priorities", [])
    tags = {tag for item in contract.get("top5", []) for tag in item.get("reason_tags", [])}
    checks = []
    for priority in priorities:
        expected_tag = _PRIORITY_TAGS.get(str(priority).lower())
        matched = bool(expected_tag and expected_tag in tags)
        checks.append({"priority": priority, "expected_tag": expected_tag, "matched": matched})
    matched_count = sum(1 for item in checks if item["matched"])
    return {"coverage": round(matched_count / len(checks), 4) if checks else None, "checks": checks}


def manual_score(manual_scores: dict[str, float] | None) -> dict[str, Any]:
    if not manual_scores:
        return {
            "average": None,
            "criteria": {
                "relevance": "Mức phù hợp với nhu cầu mô tả tự do.",
                "constraint_fit": "Có tôn trọng ngân sách, số phòng, tiện ích bắt buộc.",
                "explainability": "Lý do đề xuất rõ ràng và kiểm chứng được.",
                "diversity": "Top X có đủ lựa chọn thay thế hợp lý.",
                "trust": "Người đánh giá có sẵn sàng shortlist kết quả này không.",
            },
        }
    clipped = {key: max(0.0, min(5.0, float(value))) for key, value in manual_scores.items()}
    return {"average": round(sum(clipped.values()) / len(clipped), 3) if clipped else None, "criteria": clipped}


def evaluate_contract(
    contract: dict[str, Any],
    form: dict[str, Any],
    expected: dict[str, Any] | None,
    ground_truth_top5: list[str] | None,
    top_x: int,
    manual_scores: dict[str, float] | None = None,
) -> dict[str, Any]:
    recommended_ids = [item.get("property_id") for item in contract.get("top5", []) if item.get("property_id")]
    hard = hard_constraint_score(contract, form)
    expected_score = expected_priority_score(contract, expected)
    ir = None
    if ground_truth_top5:
        ir = {
            "precision_at_k": round(precision_at_k(recommended_ids, ground_truth_top5, top_x), 4),
            "recall_at_k": round(recall_at_k(recommended_ids, ground_truth_top5, top_x), 4),
            "ndcg_at_k": round(ndcg_at_k(recommended_ids, ground_truth_top5, top_x), 4),
            "average_precision": round(average_precision(recommended_ids, ground_truth_top5, top_x), 4),
        }
    return {
        "status": contract.get("status"),
        "recommended_ids": recommended_ids,
        "hard_constraints": hard,
        "expected_priority_coverage": expected_score,
        "ir_metrics": ir,
        "manual_evaluation": manual_score(manual_scores),
    }


def scenario_to_input(scenario: dict[str, Any]) -> tuple[dict[str, Any], str, dict[str, Any] | None, list[str] | None, str]:
    if "input" in scenario:
        form = scenario["input"]
        return form, form.get("user_need_text", ""), scenario.get("expected"), scenario.get("ground_truth_top5"), scenario.get("case_id", "case")
    hard = scenario.get("hard_constraints", {})
    form = {
        "budget_max_million": hard.get("budget_max_million"),
        "min_bedrooms": hard.get("min_bedrooms"),
        "soft_preferences": scenario.get("soft_preferences", {}),
        "user_need_text": scenario.get("user_need_text", scenario.get("name", "")),
    }
    return form, form["user_need_text"], None, scenario.get("ground_truth_top5"), scenario.get("scenario_id", "case")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/validation-cases")
def validation_cases(dataset: str = "validation_cases_v1") -> dict[str, Any]:
    path = VALIDATION_50_FILE if dataset == "validation_50_scenarios" else VALIDATION_V1_FILE
    cases = load_json(path)
    return {
        "dataset": dataset,
        "cases": [
            {
                "id": case.get("case_id", case.get("scenario_id")),
                "name": case.get("persona", case.get("name", "")),
                "group": case.get("case_group", case.get("archetype", "")),
                "input": scenario_to_input(case)[0],
                "expected": case.get("expected"),
                "ground_truth_top5": case.get("ground_truth_top5"),
            }
            for case in cases
        ],
    }


@app.post("/api/recommend")
def recommend(request: RecommendationRequest) -> dict[str, Any]:
    case_id = f"WEB_{int(time.time())}"
    return {
        "case_id": case_id,
        "results": run_selected_solutions(request.form, request.free_text, request.solution, request.top_x, case_id),
    }


@app.post("/api/validate")
def validate(request: ValidationRequest) -> dict[str, Any]:
    case_id = request.case_id or f"WEB_VAL_{int(time.time())}"
    results = run_selected_solutions(request.form, request.free_text, request.solution, request.top_x, case_id)
    evaluations = {
        key: evaluate_contract(value, request.form, request.expected, request.ground_truth_top5, request.top_x, request.manual_scores)
        for key, value in results.items()
    }
    return {"case_id": case_id, "results": results, "evaluations": evaluations}


@app.post("/api/validate-batch")
def validate_batch(request: BatchValidationRequest) -> dict[str, Any]:
    path = VALIDATION_50_FILE if request.dataset == "validation_50_scenarios" else VALIDATION_V1_FILE
    cases = load_json(path)[: request.limit]
    rows = []
    aggregate: dict[str, list[float]] = {}
    for scenario in cases:
        form, free_text, expected, ground_truth, case_id = scenario_to_input(scenario)
        results = run_selected_solutions(form, free_text, request.solution, request.top_x, case_id)
        evaluations = {
            key: evaluate_contract(value, form, expected, ground_truth, request.top_x)
            for key, value in results.items()
        }
        for key, evaluation in evaluations.items():
            aggregate.setdefault(f"{key}_hard_pass", []).append(evaluation["hard_constraints"]["pass_rate"])
            if evaluation["ir_metrics"]:
                aggregate.setdefault(f"{key}_precision", []).append(evaluation["ir_metrics"]["precision_at_k"])
                aggregate.setdefault(f"{key}_recall", []).append(evaluation["ir_metrics"]["recall_at_k"])
                aggregate.setdefault(f"{key}_ndcg", []).append(evaluation["ir_metrics"]["ndcg_at_k"])
            coverage = evaluation["expected_priority_coverage"]["coverage"]
            if coverage is not None:
                aggregate.setdefault(f"{key}_priority_coverage", []).append(coverage)
        rows.append({"case_id": case_id, "results": results, "evaluations": evaluations})
    summary = {key: round(sum(values) / len(values), 4) for key, values in aggregate.items() if values}
    return {"dataset": request.dataset, "limit": request.limit, "summary": summary, "rows": rows}
