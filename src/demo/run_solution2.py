"""Chạy Solution 2 trên validation set dùng chung của nhóm.

Mặc định chạy đúng bộ mà Solution 1 dùng để member-4 so sánh công bằng:
100 BĐS Gò Vấp/Tân Bình đã enrich + data/validation_cases_v1.json.
Ghi outputs/solution2_results.json theo output contract chung.

Dùng `--own` để chạy bộ validation riêng của Solution 2 (12 case S2_*, dataset 37 căn)
khi cần demo sâu các tính năng free-text.
"""

import argparse
import datetime
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

# Bộ dùng chung với Solution 1 (mặc định) — để member-4 so sánh cùng chuẩn
SHARED_PROPERTIES = os.path.join(DATA_DIR, "go_vap_tan_binh_100_enriched.json")
SHARED_VALIDATION = os.path.join(DATA_DIR, "validation_cases_v1.json")
SHARED_RESULTS = os.path.join(OUTPUT_DIR, "solution2_results.json")

# Bộ riêng của Solution 2 (tuỳ chọn --own)
OWN_PROPERTIES = os.path.join(DATA_DIR, "go_vap_enriched.json")
OWN_VALIDATION = os.path.join(DATA_DIR, "validation_solution2.json")
OWN_RESULTS = os.path.join(OUTPUT_DIR, "solution2_results_own.json")

LOG_DIR = os.path.join(ROOT, "logs", "solution2")


class _Tee:
    """Ghi đồng thời ra màn hình và file log."""

    def __init__(self, stream, fh):
        self._stream = stream
        self._fh = fh

    def write(self, text):
        self._stream.write(text)
        self._fh.write(text)

    def flush(self):
        self._stream.flush()
        self._fh.flush()


def main():
    ap = argparse.ArgumentParser(description="Chạy Solution 2")
    ap.add_argument("--own", action="store_true",
                    help="Chạy bộ validation riêng của Solution 2 thay vì bộ chung")
    args = ap.parse_args()

    os.makedirs(LOG_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(LOG_DIR, f"run_{'own' if args.own else 'shared'}_{stamp}.log")
    log_fh = open(log_path, "w", encoding="utf-8")
    sys.stdout = _Tee(sys.__stdout__, log_fh)

    if args.own:
        properties_file, validation_file, results_file = (
            OWN_PROPERTIES, OWN_VALIDATION, OWN_RESULTS)
    else:
        properties_file, validation_file, results_file = (
            SHARED_PROPERTIES, SHARED_VALIDATION, SHARED_RESULTS)

    with open(properties_file, encoding="utf-8") as f:
        properties = json.load(f)
    with open(validation_file, encoding="utf-8") as f:
        cases = json.load(f)

    print(f"📂 {len(properties)} BĐS | {len(cases)} validation case\n")

    results = []
    for case in cases:
        form = case["input"]
        free_text = form.get("user_need_text", "")

        t0 = time.perf_counter()
        try:
            internal = pipeline.run(form, free_text, properties)
        except Exception as e:
            # Enrichment gọi API ngoài (Overpass) nên có thể lỗi mạng/rate-limit.
            # Không để 1 case hỏng làm sập cả batch — ghi status="error" và chạy tiếp.
            # Cache đã lưu các truy vấn thành công nên chạy lại sẽ đi tiếp từ đó.
            latency_ms = round((time.perf_counter() - t0) * 1000, 1)
            results.append({
                "case_id": case["case_id"],
                "solution_id": "solution_2",
                "status": "error",
                "top5": [],
                "explanation_summary": f"Lỗi khi enrich tiện ích: {e}",
                "unsupported_requirements": [],
                "latency_ms": latency_ms,
            })
            print(f"{'='*72}")
            print(f"[{case['case_id']}] ❌ LỖI: {str(e)[:110]}")
            continue
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
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*72}")
    print(f"✅ Đã lưu {len(results)} kết quả → {results_file}")
    print(f"📝 Log → {log_path}")

    sys.stdout = sys.__stdout__
    log_fh.close()


if __name__ == "__main__":
    main()
