# Manifest Phiên Bản Dataset

## 1. Mục đích

File này khóa lại các bộ dataset mà nhóm hiện có, xác định:

- bộ nào đang dùng được ngay cho pipeline hoặc evaluation
- bộ nào là ứng viên mở rộng
- bộ nào chỉ dùng để tham khảo

## 2. Trạng thái bộ dataset hiện tại

### Dataset mở rộng 100 căn

**File:** `data/go_vap_tan_binh_100.json`

**Trạng thái:** `CLEAN_ONLY`

**Quy mô:** `100` bất động sản

**Thành phần:**
- `50` căn Gò Vấp
- `50` căn Tân Bình

**Đặc điểm:**
- đã có `property_id`
- đã có `price`, `area`, `bedrooms`, `bathrooms`
- đã có `lat/lon`
- chưa enrich lại các cột `distance_to_nearest_*`

**Khuyến nghị dùng cho:**
- benchmark quy mô lớn hơn
- mở rộng final sau khi enrich
- kiểm thử source extract

**Không nên dùng ngay cho:**
- pipeline ranking hiện tại nếu cần feature POI đầy đủ

## 3. Khuyến nghị khóa version hiện tại

Nếu nhóm cần một mốc ổn định để bắt đầu:

- **shared dataset hiện tại của phần mở rộng:** `data/go_vap_tan_binh_100.json`
- **trạng thái:** sạch về cấu trúc, chưa enrich POI

## 4. Action item cho các thành viên khác

- `Quang` (`Solution 2`) và `Phú` (`Solution 1`):
  - Có thể dùng `go_vap_tan_binh_100.json` cho các bước parser, schema, hoặc ranking chưa cần POI
  - Nếu cần ranking theo POI, phải enrich trước

- `Ấn`:
  - Có thể tham chiếu `go_vap_tan_binh_100.json` để thiết kế validation cho scope 100 căn
  - Nếu validation cần feature POI thật, phải chờ bước enrich
