# Member-3 - Tiến

File này gom các đầu ra chính cho phần việc `member-3` sau khi đã chuyển về các thư mục dùng chung ở root.

Quy ước hiện tại:
- `Solution 1`: hướng MCDA/TOPSIS của `Phú`, được đổi tên từ `Solution 3` cũ
- `Solution 2`: `Quang`
- hướng rule-based `Solution 1` cũ đã bị loại
- `Ấn`: validation / evaluation

Nguồn dữ liệu đã dùng để tổng hợp:

- `data/go_vap_tan_binh_100.json`
- `data/raw/data_public.csv`
- `data/raw/vietnam_housing_dataset.csv`

## Checklist công việc

- [x] Rà soát schema dataset chung  
  File: [dataset_schema_review.md](../dataset/dataset_schema_review.md)

- [x] Chốt danh sách cột bắt buộc cho pipeline  
  File: [dataset_schema_review.md](../dataset/dataset_schema_review.md)

- [x] Ghi chú vấn đề dữ liệu cần lưu ý  
  File: [dataset_schema_review.md](../dataset/dataset_schema_review.md)

- [x] Tạo report thô phần dataset/data preprocessing  
  File: [dataset_report_draft.md](../report/dataset_report_draft.md)

- [x] Tạo slide thô phần dataset/data overview  
  File: [dataset_slide_draft.marp.md](../slide/dataset_slide_draft.marp.md)

- [x] Ghi chú về bộ dataset mở rộng `50 Gò Vấp + 50 Tân Bình`  
  File: [dataset_expansion_note.md](../dataset/dataset_expansion_note.md)

- [x] Khóa manifest các dataset đang có  
  File: [dataset_version_manifest.md](../dataset/dataset_version_manifest.md)

- [x] Tạo handover note cho team  
  File: [handover_note_for_team.md](../notes/handover_note_for_team.md)

- [x] Lập danh sách file shared liên quan nhưng không move vào thư mục riêng  
  File: [shared_references.md](../notes/shared_references.md)

- [x] Chốt script Python dùng chung để sinh dataset 100 căn  
  File: [prepare_gv_tb_100.py](../../src/data/prepare_gv_tb_100.py)

- [x] Tạo notebook mô tả từng bước sinh JSON dataset  
  File: [prepare_gv_tb_100.ipynb](../../notebooks/prepare_gv_tb_100.ipynb)

- [x] Tạo notebook mô tả từng bước enrich bộ dataset 100 căn  
  File: [enrich_gv_tb_100.ipynb](../../notebooks/enrich_gv_tb_100.ipynb)

- [ ] Ghép `final slide draft` của cả nhóm  
  Trạng thái: chưa thể làm độc lập  
  Lý do: cần nhận slide thô từ `Quang`, `Phú`, `Ấn`

## Cấu trúc thư mục hiện tại

- `docs/dataset/`: các file liên quan đến rà soát dataset và manifest dataset
- `docs/report/`: report thô của phần việc member-3
- `docs/slide/`: slide thô của phần dataset
- `docs/notes/`: ghi chú bàn giao và danh sách file shared
- `docs/checklist/`: checklist tổng hợp đầu ra
- `notebooks/`: notebook mô tả từng bước chạy dữ liệu
- `src/data/`: script dùng chung để sinh dataset

## File riêng của member-3

### Dataset

- [dataset_schema_review.md](../dataset/dataset_schema_review.md)
- [dataset_expansion_note.md](../dataset/dataset_expansion_note.md)
- [dataset_version_manifest.md](../dataset/dataset_version_manifest.md)

### Report

- [dataset_report_draft.md](../report/dataset_report_draft.md)

### Slide

- [dataset_slide_draft.marp.md](../slide/dataset_slide_draft.marp.md)

### Notes

- [handover_note_for_team.md](../notes/handover_note_for_team.md)
- [shared_references.md](../notes/shared_references.md)

### Code dùng chung

- [prepare_gv_tb_100.py](../../src/data/prepare_gv_tb_100.py)

### Notebook

- [prepare_gv_tb_100.ipynb](../../notebooks/prepare_gv_tb_100.ipynb)
- [enrich_gv_tb_100.ipynb](../../notebooks/enrich_gv_tb_100.ipynb)

## Nguyên tắc gom file

- File mô tả, report, slide, note: đặt trong các thư mục dùng chung dưới `docs/`.
- File notebook: đặt trong `notebooks/`.
- File dùng chung cho cả nhóm: giữ nguyên vị trí cũ, tham chiếu trong [shared_references.md](../notes/shared_references.md).
