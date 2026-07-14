# Source note: Solution 1

> Cập nhật `2026-07-14`:
> Bản thiết kế ReAct/Vector Search cũ đã bị thay thế. Tài liệu active hiện tại là
> [`../Solution-1-Detail.md`](../Solution-1-Detail.md) và source triển khai nằm trong
> `src/solution1/`.

## Trạng thái hiện tại

Solution 1 hiện tại là:

```text
Form + Free-text
-> LLM reasoner + tool use
-> Guardrail grounding
-> LLM explainer
-> Output contract chung
```

Các điểm đã chốt:

- Không dùng autonomous agent tự do.
- Không dùng `vector_search` trong scope hiện tại.
- LLM reasoner bắt buộc gọi `sql_filter` trước.
- Dynamic enrichment chỉ chạy khi free-text yêu cầu tiện ích ngoài nhóm tiện ích nền.
- Top 5 cuối cùng luôn phải thuộc candidate set/database.
- LLM explainer không được gọi tool và không được đổi ranking.

## Lý do thay thế bản cũ

Bản cũ mô tả LLM Agent/ReAct loop tự do với nhiều tool, trong đó có `vector_search`. Hướng đó linh hoạt nhưng khó kiểm soát, khó validation và dễ lệch khỏi output contract chung. Vì vậy nhóm thu hẹp thành pipeline tuần tự hai LLM có guardrail để dễ chạy, dễ compare và bám dữ liệu hơn.

## File nên đọc

- `docs/Solution-1-Detail.md`
- `src/solution1/PLAN.md`
- `src/solution1/pipeline.py`
- `src/solution1/reasoner.py`
- `src/solution1/guardrail.py`
- `src/solution1/output_contract.py`
- `outputs/solution1_results.json`
