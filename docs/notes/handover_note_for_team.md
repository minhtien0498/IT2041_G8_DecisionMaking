# Ghi Chú Bàn Giao Cho Nhóm

## 1. Member-3 đã bàn giao gì

### Rà soát dataset

- Đã rà soát schema dataset chung
- Đã chốt bộ cột bắt buộc cho pipeline
- Đã ghi chú các cột null hoặc cột cần lưu ý

File:
- `docs/dataset/dataset_schema_review.md`

### Report thô phần dataset

File:
- `docs/report/dataset_report_draft.md`

### Slide thô phần dataset

File:
- `docs/slide/dataset_slide_draft.marp.md`

### Ghi chú mở rộng dataset

File:
- `docs/dataset/dataset_expansion_note.md`

### Manifest khóa version dataset

File:
- `docs/dataset/dataset_version_manifest.md`

## 2. Team nên dùng gì ngay bây giờ

Nếu cần chuẩn bị scope final lớn hơn:

- dùng `data/go_vap_tan_binh_100.json` làm bộ clean dataset chính
- nhưng cần enrich trước khi đưa vào ranking có POI

## 3. Việc member-1 và member-2 cần biết

- Dùng chung schema đã khóa trong `dataset_schema_review.md`
- Không tự đổi tên field giá, phòng ngủ, POI
- Nếu cần dataset lớn hơn, phải thông báo lại cho member-3/member-4 để cập nhật note và validation

## 4. Việc member-4 cần biết

- Nếu validation muốn cover scope `100` căn thì nên dựa trên `go_vap_tan_binh_100.json`
- Nếu validation cần dùng feature POI, cần có enrich cho bộ này trước

## 5. Phần member-3 chưa thể chốt độc lập

- Final slide draft của cả nhóm

Lý do:

- cần slide thô từ member-1
- cần slide thô từ member-2
- cần slide thô từ member-4

Khi cả nhóm bàn giao slide thô, member-3 có thể ghép final slide deck.
