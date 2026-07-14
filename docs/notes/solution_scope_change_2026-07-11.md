# Ghi Chú Thay Đổi Scope Solution

Ngày cập nhật: `2026-07-11`

## 1. Thay đổi chính

- `Solution 1` cũ dạng `rule-based filtering + weighted scoring` đã bị loại khỏi scope final.
- Lý do: hướng này bị đánh giá là quá đơn giản, thiên về bộ lọc/recommender cơ bản và chưa thể hiện rõ tinh thần `DSS with Data`.
- Theo góp ý của thầy, nhóm cần đổi sang một hướng ra quyết định rõ ràng hơn.

## 2. Quy ước mới

- `Solution 1` hiện tại là hướng pipeline tuần tự hai LLM có guardrail của `Phú`.
- Hướng này thay thế cả baseline rule-based cũ và bản đề xuất MCDA/TOPSIS trước đó.
- `Solution 2` giữ nguyên là hướng `hybrid form + free-text + enrich + rerank` của `Quang`.

## 3. Hệ quả trong repo

- Các tài liệu active của nhóm nên hiểu theo quy ước:
  - `Solution 1` = pipeline hai LLM có guardrail
  - `Solution 2` = giữ nguyên
- Các artifact của `Solution 1` cũ đã và đang được dọn khỏi phần active của repo.

## 4. Ghi chú về dữ liệu legacy

Hai file sau **chưa nên xoá ngay** vì vẫn còn đang được một số pipeline / test / demo tham chiếu:

- `data/go_vap_30.json`
- `data/go_vap_enriched.json`

Các nơi còn dùng gồm:

- `src/demo/run_solution2.py`
- `src/eval/generate_validation_set.py`
- `src/eval/evaluate_pipeline.py`
- `tests/test_pipeline_contract.py`
- `survey/index.html`

Vì vậy, hiện tại nên xem đây là `legacy but still in use`, không phải `safe to delete`.
