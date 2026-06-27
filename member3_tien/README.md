# Member-3 - Tiến

Thư mục này gom các đầu ra chính cho phần việc `member-3`.

Nguồn dữ liệu đã dùng để tổng hợp:

- `data/go_vap_tan_binh_100.json`
- `docs/data_public.csv`
- `docs/vietnam_housing_dataset.csv`

## Checklist công việc

- [x] Rà soát schema dataset chung  
  File: [dataset/dataset_schema_review.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/dataset/dataset_schema_review.md)

- [x] Chốt danh sách cột bắt buộc cho pipeline  
  File: [dataset/dataset_schema_review.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/dataset/dataset_schema_review.md)

- [x] Ghi chú vấn đề dữ liệu cần lưu ý  
  File: [dataset/dataset_schema_review.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/dataset/dataset_schema_review.md)

- [x] Tạo report thô phần dataset/data preprocessing  
  File: [report/dataset_report_draft.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/report/dataset_report_draft.md)

- [x] Tạo slide thô phần dataset/data overview  
  File: [slide/dataset_slide_draft.marp.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/slide/dataset_slide_draft.marp.md)

- [x] Ghi chú về bộ dataset mở rộng `50 Gò Vấp + 50 Tân Bình`  
  File: [dataset/dataset_expansion_note.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/dataset/dataset_expansion_note.md)

- [x] Khóa manifest các dataset đang có  
  File: [dataset/dataset_version_manifest.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/dataset/dataset_version_manifest.md)

- [x] Tạo handover note cho team  
  File: [notes/handover_note_for_team.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/notes/handover_note_for_team.md)

- [x] Lập danh sách file shared liên quan nhưng không move vào thư mục riêng  
  File: [notes/shared_references.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/notes/shared_references.md)

- [x] Tạo code Python riêng có chú thích cho phần mở rộng dataset 100 căn  
  File: [code/prepare_gv_tb_100_member3.py](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/code/prepare_gv_tb_100_member3.py)

- [x] Tạo notebook mô tả từng bước sinh JSON dataset  
  File: [notebook/prepare_gv_tb_100.ipynb](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/notebook/prepare_gv_tb_100.ipynb)

- [ ] Ghép `final slide draft` của cả nhóm  
  Trạng thái: chưa thể làm độc lập  
  Lý do: cần nhận slide thô từ member-1, member-2, member-4

## Cấu trúc thư mục

- `dataset/`: các file liên quan đến rà soát dataset và manifest dataset
- `report/`: report thô của phần việc member-3
- `slide/`: slide thô của phần dataset
- `notes/`: ghi chú bàn giao và danh sách file shared
- `code/`: code riêng của member-3
- `notebook/`: notebook mô tả từng bước chạy dữ liệu

## File riêng của member-3

### Dataset

- [dataset/dataset_schema_review.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/dataset/dataset_schema_review.md)
- [dataset/dataset_expansion_note.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/dataset/dataset_expansion_note.md)
- [dataset/dataset_version_manifest.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/dataset/dataset_version_manifest.md)

### Report

- [report/dataset_report_draft.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/report/dataset_report_draft.md)

### Slide

- [slide/dataset_slide_draft.marp.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/slide/dataset_slide_draft.marp.md)

### Notes

- [notes/handover_note_for_team.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/notes/handover_note_for_team.md)
- [notes/shared_references.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/notes/shared_references.md)

### Code

- [code/prepare_gv_tb_100_member3.py](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/code/prepare_gv_tb_100_member3.py)

### Notebook

- [notebook/prepare_gv_tb_100.ipynb](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/notebook/prepare_gv_tb_100.ipynb)

## Nguyên tắc gom file

- File riêng của member-3: đặt trong thư mục này.
- File dùng chung cho cả nhóm: giữ nguyên vị trí cũ, chỉ tham chiếu trong [notes/shared_references.md](/Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/member3_tien/notes/shared_references.md).
