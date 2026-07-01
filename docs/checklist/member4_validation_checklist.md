# Member-4 - Validation And Evaluation

File này gom phần việc chính của `member-4`.

## Checklist công việc

- [x] Chốt `output contract` chung
  File: [output_contract_shared.md](../output_contract_shared.md)

- [x] Tạo `validation set` bản 1
  File: [validation_cases_v1.json](../../data/validation_cases_v1.json)

- [x] Chốt rubric đánh giá
  File: [validation_rubric.md](../validation_rubric.md)

- [x] Tạo bảng compare output giữa các solution
  File: [solution_comparison_template.md](../solution_comparison_template.md)

- [ ] Nhận output từ member-1
  Kỳ vọng: đúng schema contract chung

- [ ] Nhận output từ member-2
  Kỳ vọng: đúng schema contract chung

- [ ] Chạy validation và tổng hợp kết quả
  File tham chiếu hiện có:
  - [outputs/validation_report.md](../../outputs/validation_report.md)
  - [outputs/validation_summary.json](../../outputs/validation_summary.json)

- [ ] Viết phần `Validation / Evaluation / Comparison` cho report

- [ ] Chuẩn bị 1-2 slide cho phần `Validation / Evaluation / Comparison`

## Đầu ra cần bàn giao tuần 1

- `output contract` chung đã chốt
- `validation set` bản 1
- `rubric` đánh giá
- danh sách `risk` khi so sánh 2 solution

## Đầu ra cần bàn giao tuần 2

- bảng compare kết quả chạy thật
- nhận xét solution nào tốt hơn theo từng tiêu chí
- slide và nội dung report phần validation

## Risk cần theo dõi

- member-1 và member-2 xuất lệch schema
- dataset `100` căn chưa được migrate đồng bộ vào toàn pipeline
- synthetic validation chưa đủ mạnh để chứng minh chất lượng với người dùng thật
- free-text có nhiều nhu cầu `unsupported`, dễ làm compare thiếu công bằng

## File nên mở đầu tiên

- [docs/source_notes/Implementation-Plan.md](../source_notes/Implementation-Plan.md)
- [docs/validation_dataset_plan.md](../validation_dataset_plan.md)
- [docs/solution_verification_plan.md](../solution_verification_plan.md)
- [docs/survey_validation_plan.md](../survey_validation_plan.md)
- [docs/output_contract_shared.md](../output_contract_shared.md)

