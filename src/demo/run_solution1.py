"""Chạy Solution 1 (Sequential 2-LLM Pipeline) trên validation set.

Load 100 BĐS Gò Vấp/Tân Bình đã enrich + data/validation_cases_v1.json vào Postgres,
chạy pipeline từng case với API key thật (OpenRouter + Mapbox), in tóm tắt reasoning/top5,
ghi outputs/solution1_results.json (theo output contract chung).
"""

import json
import os
import sys
import time

# Cho phép import package src.solution1 khi chạy trực tiếp script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.solution1 import db, pipeline  # noqa: E402
from src.solution1.llm_client import OpenRouterLLMClient  # noqa: E402
from src.solution1.output_contract import to_contract  # noqa: E402

DATA_DIR = os.path.join(ROOT, "data")
OUTPUT_DIR = os.path.join(ROOT, "outputs")
PROPERTIES_FILE = os.path.join(DATA_DIR, "go_vap_tan_binh_100_enriched.json")
VALIDATION_FILE = os.path.join(DATA_DIR, "validation_cases_v1.json")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "solution1_results.json")


def main():
    limit = int(os.environ.get("SOLUTION1_DEMO_LIMIT", "0")) or None
    results_file = os.environ.get("SOLUTION1_RESULTS_FILE", RESULTS_FILE)

    with open(VALIDATION_FILE, encoding="utf-8") as f:
        cases = json.load(f)
    if limit:
        cases = cases[:limit]

    with db.get_connection() as conn:
        db.init_schema(conn)
        n = db.load_properties(conn, PROPERTIES_FILE)
        print(f"📂 {n} BĐS đã load vào Postgres | {len(cases)} validation case\n")

        reasoning_client = OpenRouterLLMClient("reasoning")
        explanation_client = OpenRouterLLMClient("explanation")

        results = []
        for case in cases:
            form = case["input"]
            free_text = form.get("user_need_text", "")

            t0 = time.perf_counter()
            internal = pipeline.run(
                form, free_text, conn,
                reasoning_client=reasoning_client, explanation_client=explanation_client,
            )
            latency_ms = round((time.perf_counter() - t0) * 1000, 1)

            contract = to_contract(case["case_id"], internal, latency_ms)
            results.append(contract)

            top_ids = " > ".join(t["property_id"] for t in contract["top5"])
            print(f"{'='*72}")
            print(f"[{case['case_id']}] {case.get('case_group', '')} | \"{free_text}\"")
            print(f"  status={contract['status']} | models={contract['models_used']} | {latency_ms}ms")
            print(f"  Top5: {top_ids}")
            print(f"  → {contract['explanation_summary']}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*72}")
    print(f"✅ Đã lưu {len(results)} kết quả → {results_file}")


if __name__ == "__main__":
    main()
