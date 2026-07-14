# Shared Output Contract

File này là bản chốt schema output dùng chung cho hai solution chính và phần validation.

Quy ước hiện tại:
- `Solution 1`: pipeline tuần tự hai LLM có guardrail của `Phú`
- `Solution 2`: hướng của `Quang`
- hướng rule-based `Solution 1` cũ đã bị loại khỏi scope final
- `Ấn`: phụ trách validation / evaluation

Mục tiêu:
- Hai solution phải xuất cùng format.
- Member-4 có thể validate, so sánh, và ghép bảng kết quả mà không cần viết mapper riêng cho từng solution.

## 1. Schema bắt buộc

Mỗi case chạy qua một solution phải trả ra object dạng:

```json
{
  "case_id": "VAL_001",
  "solution_id": "solution_1",
  "status": "ok",
  "top5": [
    {
      "rank": 1,
      "property_id": "GV_008",
      "total_score": 0.87,
      "hard_constraint_pass": true,
      "reason_tags": ["near_school", "near_park"]
    }
  ],
  "explanation_summary": "Top 1 cân bằng tốt giữa trường học, công viên và ngân sách.",
  "unsupported_requirements": [],
  "latency_ms": 1820
}
```

## 2. Field bắt buộc mức top-level

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `case_id` | string | ID của validation case |
| `solution_id` | string | ID solution, ví dụ `solution_1`, `solution_2` |
| `status` | string | Trạng thái chạy, ví dụ `ok`, `no_candidate`, `error` |
| `top5` | array | Danh sách tối đa `5` BĐS được đề xuất |
| `explanation_summary` | string | Tóm tắt giải thích ngắn gọn |
| `unsupported_requirements` | array[string] | Các yêu cầu không đo được / chưa hỗ trợ |
| `latency_ms` | number | Thời gian chạy cho case |

## 3. Field bắt buộc trong `top5`

| Field | Kiểu | Ý nghĩa |
|---|---|---|
| `rank` | integer | Hạng bắt đầu từ `1`, tăng liên tục |
| `property_id` | string | ID BĐS |
| `total_score` | number | Điểm cuối cùng dùng để xếp hạng |
| `hard_constraint_pass` | boolean | Có thỏa ràng buộc cứng không |
| `reason_tags` | array[string] | Tag ngắn mô tả lý do đề xuất |

Quy tắc:
- `top5` có thể ít hơn `5` nếu không đủ candidate.
- `top5` phải được sắp xếp giảm dần theo `total_score`.
- Không được có `property_id` trùng trong cùng một `top5`.

## 4. Field mở rộng được phép thêm

Các field sau được phép có, nhưng không bắt buộc:

```json
{
  "base_score": 0.541,
  "additional_score": 0.711,
  "why_recommended": "Giá tốt, gần trường và còn trong ngân sách.",
  "tradeoff": "Diện tích nhỏ hơn lựa chọn hạng 2.",
  "dynamic_attributes": {
    "nearby_market_count_within_1000m": 3
  },
  "title": "SIEU PHAM TRUNG TAM GO VAP",
  "price_billion_vnd": 4.55
}
```

Nguyên tắc:
- Được thêm field mở rộng để debug hoặc giải thích.
- Không được bỏ field bắt buộc.
- Member-4 chỉ dùng field bắt buộc để compare công bằng giữa các solution.

## 5. Mapping trạng thái

| `status` | Khi nào dùng |
|---|---|
| `ok` | Pipeline chạy bình thường và có output hợp lệ |
| `no_candidate` | Không có BĐS nào qua lọc cứng |
| `error` | Pipeline lỗi hoặc output không hoàn tất |

Nếu `status = no_candidate`:
- `top5` nên là `[]`
- `explanation_summary` phải nói rõ lý do
- `unsupported_requirements` vẫn phải giữ nếu có

## 6. Nguồn tham chiếu trong repo

Schema này khớp với:
- [docs/source_notes/Implementation-Plan.md](source_notes/Implementation-Plan.md)
- [docs/Solution-1-Detail.md](Solution-1-Detail.md)
- [docs/solution2_implementation_guide.md](solution2_implementation_guide.md)
- [src/solution1/output_contract.py](../src/solution1/output_contract.py)
- [src/solution2/output_contract.py](../src/solution2/output_contract.py)
- [tests/test_pipeline_contract.py](../tests/test_pipeline_contract.py)

## 7. Definition of done cho `Quang` và `Phú`

Mỗi solution được xem là đã nối đúng contract khi:
- Xuất được `JSON` đúng schema trên.
- `top5[].rank` tăng liên tục từ `1`.
- `top5` sắp xếp đúng theo `total_score`.
- Có `unsupported_requirements` nếu input có nhu cầu không đo được.
- Member-4 đọc file output mà không cần viết code chuyển đổi riêng.
