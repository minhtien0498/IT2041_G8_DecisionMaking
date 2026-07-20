"""Chạy Solution 1 (Sequential 2-LLM Pipeline) trên validation set.

Load 100 BĐS Gò Vấp/Tân Bình đã enrich + data/validation_cases_v1.json vào Postgres,
chạy pipeline từng case với API key thật (OpenRouter + mapbox/geoapify/overpass tùy
`SOLUTION1_ENRICHMENT_PROVIDER`), in tóm tắt reasoning/top5, ghi
outputs/solution1_results.json (theo output contract chung).
"""

import json
import os
import sys
import time

# Cho phép import package src.solution1 khi chạy trực tiếp script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.solution1 import db, enrichment_provider, pipeline  # noqa: E402
from src.solution1.llm_client import OpenRouterLLMClient  # noqa: E402
from src.solution1.output_contract import to_contract  # noqa: E402

DATA_DIR = os.path.join(ROOT, "data")
OUTPUT_DIR = os.path.join(ROOT, "outputs")
VALIDATION_FILE = os.path.join(DATA_DIR, "validation_cases_v1.json")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "solution1_results.json")


def _render_explanation_markdown(case_id, free_text, contract):
    """Dựng lại đúng format outputs/explanations/V1_*.md (xem commit 74b2b5c)."""
    lines = [f"# {case_id}", "", f"> {free_text}", "", "## Gợi ý bất động sản (Top 5)", ""]
    for item in contract["top5"]:
        price = item.get("price_billion_vnd")
        price_str = f" ({price} tỷ)" if price is not None else ""
        lines.append(
            f"**#{item['rank']} {item['property_id']}** — {item.get('title', '')}"
            f"{price_str} — điểm {item['total_score']}"
        )
        lines.append("")
        lines.append(f"- Lý do: {', '.join(item.get('reason_tags', []))}")
        lines.append(f"- {item.get('why_recommended', '')}")
        lines.append(f"- Đánh đổi: {item.get('tradeoff', '')}")
        lines.append("")
    lines.append("## Giải thích")
    lines.append("")
    lines.append(contract.get("explanation_summary", ""))
    return "\n".join(lines) + "\n"


def _load_existing_results(results_file):
    """Đọc kết quả đã lưu trước đó (nếu có) -> dict case_id -> contract, để resume."""
    if not os.path.exists(results_file):
        return {}
    with open(results_file, encoding="utf-8") as f:
        existing = json.load(f)
    return {item["case_id"]: item for item in existing}


def main():
    limit = int(os.environ.get("SOLUTION1_DEMO_LIMIT", "0")) or None
    case_id_filter = os.environ.get("SOLUTION1_DEMO_CASE_ID", "").strip() or None
    case_ids_filter = os.environ.get("SOLUTION1_DEMO_CASE_IDS", "").strip() or None
    results_file = os.environ.get("SOLUTION1_RESULTS_FILE", RESULTS_FILE)
    explanations_dir = os.environ.get("SOLUTION1_EXPLANATIONS_DIR", "").strip() or None
    # Nếu results_file đã có sẵn kết quả (status=ok) cho 1 case_id, BỎ QUA case đó thay vì
    # gọi lại pipeline — tránh mất công/API quota khi resume sau khi 1 lần chạy trước bị
    # kẹt/kill giữa chừng (xem /memories/repo/solution1_llm_notes.md, mục 2026-07-19).
    # Set SOLUTION1_FORCE_RERUN=1 để tắt hành vi này (luôn chạy lại toàn bộ).
    force_rerun = os.environ.get("SOLUTION1_FORCE_RERUN", "").strip() == "1"

    # Nguồn enrichment (mapbox/geoapify/overpass) chọn qua SOLUTION1_ENRICHMENT_PROVIDER
    # (mặc định "mapbox") — quyết định luôn cả file JSON nạp vào DB lẫn API thật mà
    # fetch_nearby_custom/get_distance_to_place gọi (xem enrichment_provider.py).
    provider = enrichment_provider.get_provider()
    properties_file = enrichment_provider.get_properties_file(ROOT)

    with open(VALIDATION_FILE, encoding="utf-8") as f:
        cases = json.load(f)
    if case_id_filter:
        cases = [c for c in cases if c["case_id"] == case_id_filter]
        if not cases:
            raise SystemExit(f"Không tìm thấy case_id={case_id_filter!r} trong {VALIDATION_FILE}")
    elif case_ids_filter:
        wanted = {cid.strip() for cid in case_ids_filter.split(",") if cid.strip()}
        cases = [c for c in cases if c["case_id"] in wanted]
    elif limit:
        cases = cases[:limit]

    all_results = {} if force_rerun else _load_existing_results(results_file)
    # Chỉ coi case là "đã xong" nếu status=="ok" — case status="error" (vd LLM pool lỗi
    # hết/quota cạn) vẫn cần chạy lại khi resume, không được bỏ qua như case thành công.
    pending_cases = [
        c for c in cases
        if force_rerun or all_results.get(c["case_id"], {}).get("status") != "ok"
    ]
    n_skipped = len(cases) - len(pending_cases)
    if n_skipped:
        print(f"⏭️  Bỏ qua {n_skipped} case đã có kết quả sẵn trong {results_file} (resume)")

    with db.get_connection() as conn:
        db.init_schema(conn)
        n = db.load_properties(conn, properties_file)
        print(f"📂 [{provider}] {n} BĐS đã load vào Postgres | {len(cases)} validation case "
              f"({len(pending_cases)} sẽ chạy)\n")

        reasoning_client = OpenRouterLLMClient("reasoning")
        explanation_client = OpenRouterLLMClient("explanation")

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        for case in pending_cases:
            form = case["input"]
            free_text = form.get("user_need_text", "")

            t0 = time.perf_counter()
            internal = pipeline.run(
                form, free_text, conn,
                reasoning_client=reasoning_client, explanation_client=explanation_client,
            )
            latency_ms = round((time.perf_counter() - t0) * 1000, 1)

            contract = to_contract(case["case_id"], internal, latency_ms)
            all_results[case["case_id"]] = contract

            if explanations_dir:
                os.makedirs(explanations_dir, exist_ok=True)
                md = _render_explanation_markdown(case["case_id"], free_text, contract)
                md_path = os.path.join(explanations_dir, f"{case['case_id']}.md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md)

            top_ids = " > ".join(t["property_id"] for t in contract["top5"])
            print(f"{'='*72}")
            print(f"[{case['case_id']}] {case.get('case_group', '')} | \"{free_text}\"")
            print(f"  status={contract['status']} | models={contract['models_used']} | {latency_ms}ms")
            print(f"  tool_calls_summary={contract['tool_calls_summary']}")
            print(f"  Top5: {top_ids}")
            print(f"  → {contract['explanation_summary']}")

            # Lưu ngay sau MỖI case (không chờ hết cả batch) — nếu process bị kẹt/kill
            # giữa chừng (vd LLM hang), lần chạy lại sau chỉ mất tối đa 1 case dở dang
            # thay vì mất sạch toàn bộ tiến độ đã tích luỹ.
            ordered = [all_results[c["case_id"]] for c in cases if c["case_id"] in all_results]
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(ordered, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*72}")
    print(f"✅ Đã lưu {len(all_results)} kết quả → {results_file}")


if __name__ == "__main__":
    main()
