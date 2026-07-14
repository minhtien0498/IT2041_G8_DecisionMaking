# Ghi Chú Bàn Giao Cho Nhóm

Quy ước hiện tại:
- `Solution 1`: pipeline tuần tự hai LLM có guardrail của `Phú`
- `Solution 2`: `Quang`
- hướng rule-based `Solution 1` cũ đã bị loại khỏi scope final
- `Tiến`: data / enrich / dataset
- `Ấn`: validation / evaluation

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

## 3. Việc Quang và Phú cần biết

- Dùng chung schema đã khóa trong `dataset_schema_review.md`
- Không tự đổi tên field giá, phòng ngủ, POI
- Nếu cần dataset lớn hơn, phải thông báo lại cho `Tiến` / `Ấn` để cập nhật note và validation

## 4. Việc Ấn cần biết

- Nếu validation muốn cover scope `100` căn thì nên dựa trên `go_vap_tan_binh_100.json`
- Nếu validation cần dùng feature POI, cần có enrich cho bộ này trước

## 5. Phần Tiến chưa thể chốt độc lập

- Final slide draft của cả nhóm

Lý do:

- cần slide thô từ `Quang`
- cần slide thô từ `Phú`
- cần slide thô từ `Ấn`

Khi cả nhóm bàn giao slide thô, `Tiến` có thể ghép final slide deck.
