"""Chạy Solution 2 trên validation set có free-text.

Load 37 BĐS Gò Vấp đã enrich + data/validation_solution2.json,
chạy pipeline từng case, in tóm tắt và ghi outputs/solution2_results.json
(theo output contract chung).
"""

import json
import os
import sys
import time

# Cho phép import package src.solution2 khi chạy trực tiếp script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.solution2 import pipeline  # noqa: E402
from src.solution2.output_contract import to_contract  # noqa: E402

DATA_DIR = os.path.join(ROOT, "data")
OUTPUT_DIR = os.path.join(ROOT, "outputs")
PROPERTIES_FILE = os.path.join(DATA_DIR, "go_vap_enriched.json")
VALIDATION_FILE = os.path.join(DATA_DIR, "validation_solution2.json")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "solution2_results.json")


def main():
    with open(PROPERTIES_FILE, encoding="utf-8") as f:
        properties = json.load(f)
    with open(VALIDATION_FILE, encoding="utf-8") as f:
        cases = json.load(f)

    print(f"📂 {len(properties)} BĐS | {len(cases)} validation case\n")

    results = []
    for case in cases:
        form = case["input"]
        free_text = form.get("user_need_text", "")

        t0 = time.perf_counter()
        internal = pipeline.run(form, free_text, properties)
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)

        contract = to_contract(case["case_id"], internal, latency_ms)
        results.append(contract)

        parsed = internal["parsed"]
        top_ids = " > ".join(t["property_id"] for t in contract["top5"])
        print(f"{'='*72}")
        print(f"[{case['case_id']}] {case['case_group']} | \"{free_text}\"")
        print(f"  parsed: soft={len(parsed.soft)} hard={len(parsed.hard)} "
              f"unsupported={len(parsed.unsupported)} duplicates={len(parsed.duplicates)}")
        print(f"  Top5: {top_ids}")
        print(f"  → {contract['explanation_summary']}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*72}")
    print(f"✅ Đã lưu {len(results)} kết quả → {RESULTS_FILE}")


if __name__ == "__main__":
    main()
