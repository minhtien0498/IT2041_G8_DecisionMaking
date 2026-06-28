# 📚 Mục lục tài liệu — Nhóm 8 (IT2041)

Index toàn bộ tài liệu trong `docs/`. Đề tài: **Hệ thống tư vấn chọn bất động sản thông minh ở TP.HCM**.

> Quy ước tên: dùng **Solution 1 / 2 / 3** (không dùng "5.1/5.2/5.3"). Bản cũ nằm trong [`/archive`](../archive/).

---

## 1. Tổng quan đề tài
| Tài liệu | Nội dung |
|---|---|
| [Final-Project.md](Final-Project.md) | Mô tả đề tài, input/output, nguồn dữ liệu, 3 solutions, tiêu chí đánh giá |
| [de-tai-bds.md](de-tai-bds.md) | Bản giới thiệu đề tài (ngắn) |
| [../PROJECT_PLAN.md](../PROJECT_PLAN.md) | Kế hoạch phát triển (roadmap midterm/final) |
| [source_notes/Implementation-Plan.md](source_notes/Implementation-Plan.md) | **Kế hoạch triển khai theo tuần + phân công 4 member** (active) |

## 2. Ba giải pháp (Solution Details)
| Tài liệu | Hướng tiếp cận |
|---|---|
| [Solution-1-Detail.md](Solution-1-Detail.md) | **Solution 1** — Rule-based: Form → Inference Engine → LLM giải thích |
| [Solution-2-Detail.md](Solution-2-Detail.md) | **Solution 2** — Hybrid: Form + free-text → LLM parse → enrich → re-rank → giải thích |
| [Solution-3-Detail.md](Solution-3-Detail.md) | **Solution 3** — Data-driven MCDA/TOPSIS + sensitivity analysis |
| [solution_evaluation.md](solution_evaluation.md) | Đánh giá & so sánh 3 hướng, khuyến nghị chọn solution |

## 3. Triển khai Solution 2 (member-2)
| Tài liệu | Nội dung |
|---|---|
| [solution2_implementation_guide.md](solution2_implementation_guide.md) | **Hướng dẫn thực hành**: chạy, cấu trúc package, mở rộng (cắm LLM/Map API), test |
| [superpowers/specs/2026-06-28-solution2-design.md](superpowers/specs/2026-06-28-solution2-design.md) | Spec thiết kế Solution 2 (đã duyệt) |
| → code | [`../src/solution2/`](../src/solution2/) · [`../src/demo/run_solution2.py`](../src/demo/run_solution2.py) · [`../tests/`](../tests/) |

## 4. Dữ liệu (member-3)
| Tài liệu | Nội dung |
|---|---|
| [dataset_recommendation.md](dataset_recommendation.md) | Đề xuất nguồn dataset |
| [data_preparation_plan.md](data_preparation_plan.md) | Kế hoạch chuẩn bị/tiền xử lý dữ liệu |
| [data_expansion_guide.md](data_expansion_guide.md) | Hướng dẫn mở rộng dữ liệu & kiểm định nhu cầu |
| → thư mục riêng | [`../member3_tien/`](../member3_tien/) (report/slide/notes nháp của member-3) |

## 5. Validation & Đánh giá (member-4)
| Tài liệu | Nội dung |
|---|---|
| [validation_dataset_plan.md](validation_dataset_plan.md) | Kế hoạch xây validation set (properties + scenarios + relevance labels) |
| [validation_dataset_search.md](validation_dataset_search.md) | Khảo sát nguồn validation dataset |
| [survey_validation_plan.md](survey_validation_plan.md) | Kế hoạch khảo sát người dùng để chấm relevance |
| [solution_verification_plan.md](solution_verification_plan.md) | Kế hoạch kiểm chứng/so sánh các solution |
| [validation_push_note.md](validation_push_note.md) | Ghi chú việc đã làm/cần làm cho validation |
| [source_notes/Validation-Set-Template.md](source_notes/Validation-Set-Template.md) | Mẫu cấu trúc một validation case |

## 6. Slide trình bày
| Tài liệu | Nội dung |
|---|---|
| [slides_sol1_vs_sol2.marp.md](slides_sol1_vs_sol2.marp.md) | So sánh Solution 1 vs Solution 2 (bản mới, đầy đủ) |
| [slide_solutions_review.marp.md](slide_solutions_review.marp.md) | Slide review giải pháp 1 & 2 (framing System Prompt + Few-shot) |

## 7. Tài liệu nguồn / nháp
| Thư mục | Nội dung |
|---|---|
| [source_notes/](source_notes/) | Ghi chú gốc & thiết kế giải thuật. Gồm [Mermaid.md](source_notes/Mermaid.md) (sơ đồ pipeline) và bản thiết kế **thay thế** cho Solution 1 ([source_notes/Solution-1-Detail.md](source_notes/Solution-1-Detail.md) — hướng LLM Agent/ReAct) |
| [../archive/](../archive/) | Tài liệu cũ đã thay thế (naming "5.x", slide/detail trùng) — đóng băng, không dùng |

---

### ⚠️ Còn cần nhóm chốt
- **Solution 1**: 2 bản thiết kế khác nhau — [Solution-1-Detail.md](Solution-1-Detail.md) (rule-based, khớp code hiện tại) vs [source_notes/Solution-1-Detail.md](source_notes/Solution-1-Detail.md) (LLM Agent). Member-1 chọn hướng chính.
- **Final-Project**: [Final-Project.md](Final-Project.md) vs [source_notes/Final-Project.md](source_notes/Final-Project.md) — mỗi bản có phần riêng, nên gộp thành 1 bản chuẩn.
