# 📚 Mục lục tài liệu — Nhóm 8 (IT2041)

Index toàn bộ tài liệu trong `docs/`. Đề tài: **Hệ thống tư vấn chọn bất động sản thông minh ở TP.HCM**.

> Quy ước tên active hiện tại: dùng **Solution 1 / 2** cho hai hướng final đang theo.
>
> Quy ước hiện tại để làm final:
> - `Solution 1`: hướng MCDA/TOPSIS của `Phú`, được đổi tên từ `Solution 3` cũ
> - `Solution 2`: hướng hybrid form + free-text của `Quang`
> - hướng rule-based `Solution 1` cũ đã bị loại và chỉ còn ý nghĩa lịch sử
> - `Tiến`: dữ liệu / enrich / dataset
> - `Ấn`: validation / evaluation

---

## 1. Tổng quan đề tài
| Tài liệu | Nội dung |
|---|---|
| [Final-Project.md](Final-Project.md) | Mô tả đề tài, input/output, nguồn dữ liệu, 2 hướng final chính và tiêu chí đánh giá |
| [../PROJECT_PLAN.md](../PROJECT_PLAN.md) | Kế hoạch phát triển (roadmap midterm/final) |
| [source_notes/Implementation-Plan.md](source_notes/Implementation-Plan.md) | Kế hoạch triển khai gốc theo tuần + phân công 4 member (mang tính lịch sử, còn giữ để đối chiếu) |
| [final_timeline_2026-07-24.md](final_timeline_2026-07-24.md) | Timeline cập nhật mới nhất cho mốc báo cáo `24/07/2026` |
| [notes/solution_scope_change_2026-07-11.md](notes/solution_scope_change_2026-07-11.md) | Ghi chú chính thức về việc đổi scope và đổi tên Solution 1 |

## 2. Hai hướng final
| Tài liệu | Hướng tiếp cận |
|---|---|
| [Solution-1-Detail.md](Solution-1-Detail.md) | **Solution 1** — Data-driven MCDA/TOPSIS + sensitivity analysis |
| [Solution-2-Detail.md](Solution-2-Detail.md) | **Solution 2** — Hybrid: Form + free-text → LLM parse → enrich → re-rank → giải thích |
| [solution_evaluation.md](solution_evaluation.md) | Đánh giá & so sánh 3 hướng, khuyến nghị chọn solution |

## 3. Triển khai Solution 2 (Quang)
| Tài liệu | Nội dung |
|---|---|
| [solution2_implementation_guide.md](solution2_implementation_guide.md) | **Hướng dẫn thực hành**: chạy, cấu trúc package, mở rộng (cắm LLM/Map API), test |
| [superpowers/specs/2026-06-28-solution2-design.md](superpowers/specs/2026-06-28-solution2-design.md) | Spec thiết kế Solution 2 (đã duyệt) |
| → code | [`../src/solution2/`](../src/solution2/) · [`../src/demo/run_solution2.py`](../src/demo/run_solution2.py) · [`../tests/`](../tests/) |

## 4. Dữ liệu (Tiến)
| Tài liệu | Nội dung |
|---|---|
| [dataset_recommendation.md](dataset_recommendation.md) | Đề xuất nguồn dataset |
| [data_preparation_plan.md](data_preparation_plan.md) | Kế hoạch chuẩn bị/tiền xử lý dữ liệu |
| [data_expansion_guide.md](data_expansion_guide.md) | Hướng dẫn mở rộng dữ liệu & kiểm định nhu cầu |
| [dataset/dataset_schema_review.md](dataset/dataset_schema_review.md) | Rà soát schema dataset 100 căn dùng chung |
| [report/dataset_report_draft.md](report/dataset_report_draft.md) | Bản thô báo cáo phần dataset/data preprocessing |
| [slide/dataset_slide_draft.marp.md](slide/dataset_slide_draft.marp.md) | Slide thô phần dataset |
| [checklist/member3_dataset_checklist.md](checklist/member3_dataset_checklist.md) | Checklist đầu ra và link nhanh đến toàn bộ phần Tiến |

## 5. Validation & Đánh giá (Ấn)
| Tài liệu | Nội dung |
|---|---|
| [output_contract_shared.md](output_contract_shared.md) | Output contract chung cho hai solution chính và phần validation |
| [validation_dataset_plan.md](validation_dataset_plan.md) | Kế hoạch xây validation set (properties + scenarios + relevance labels) |
| [validation_dataset_search.md](validation_dataset_search.md) | Khảo sát nguồn validation dataset |
| [survey_validation_plan.md](survey_validation_plan.md) | Kế hoạch khảo sát người dùng để chấm relevance |
| [solution_verification_plan.md](solution_verification_plan.md) | Kế hoạch kiểm chứng/so sánh các solution |
| [validation_rubric.md](validation_rubric.md) | Rubric chấm và thứ tự ưu tiên metric của Ấn |
| [source_notes/Validation-Set-Template.md](source_notes/Validation-Set-Template.md) | Mẫu cấu trúc một validation case |
| [solution_comparison_template.md](solution_comparison_template.md) | Khung bảng compare kết quả giữa các solution |
| [checklist/member4_validation_checklist.md](checklist/member4_validation_checklist.md) | Checklist đầu ra và đầu việc chính của Ấn |
## 6. Tài liệu nguồn / nháp
| Thư mục | Nội dung |
|---|---|
| [source_notes/](source_notes/) | Ghi chú gốc & thiết kế giải thuật. Gồm [Mermaid.md](source_notes/Mermaid.md) (sơ đồ pipeline) và các bản thiết kế đã thay thế |
| [../archive/](../archive/) | Tài liệu cũ đã thay thế (naming "5.x", slide/detail trùng) — đóng băng, không dùng |

---

### ⚠️ Ghi chú đổi tên
- `Solution 1` hiện tại là tên mới của hướng MCDA/TOPSIS trước đây từng gọi là `Solution 3`.
- Hướng rule-based `Solution 1` cũ đã bị loại khỏi scope final và đã được dọn khỏi phần active của repo.
- Khi viết slide/report, nhóm nên bám đúng quy ước: `Phú = Solution 1`, `Quang = Solution 2`.
