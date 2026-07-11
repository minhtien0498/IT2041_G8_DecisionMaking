# Rà Soát Schema Dataset

## 1. Dataset chính cho phần việc của member-3 (`Tiến`)

Dataset chính hiện tại của phần này là:

- File chính: `data/go_vap_tan_binh_100.json`
- Số mẫu: `100` bất động sản
- Thành phần: `50` căn ở `Gò Vấp` và `50` căn ở `Tân Bình`
- Mục đích: mở rộng quy mô dataset so với bản cũ, chuẩn bị cho scope final lớn hơn

Dataset mở rộng để tham khảo hoặc scale-up:

- `data/raw/data_public.csv`: `51,304` dòng, `28` cột
- `data/raw/vietnam_housing_dataset.csv`: `30,229` dòng, `12` cột

## 2. Schema chính của `data/go_vap_tan_binh_100.json`

Tổng số cột hiện có: `32`

### 2.1. Định danh và thông tin cơ bản

- `property_id`
- `title`
- `district`
- `ward`
- `location_raw`

### 2.2. Giá và thông tin cấu trúc

- `price_million_vnd`
- `price_billion_vnd`
- `area_m2`
- `price_per_m2_million`
- `bedrooms`
- `bathrooms`
- `floors`
- `direction`
- `position`
- `description_snippet`

### 2.3. Tọa độ

- `latitude`
- `longitude`

### 2.4. Cột khoảng cách POI

- `distance_to_nearest_school_m`
- `distance_to_nearest_park_m`
- `distance_to_nearest_hospital_m`
- `distance_to_nearest_supermarket_m`
- `distance_to_nearest_boulevard_m`

## 3. Danh sách cột bắt buộc cho pipeline

Đây là bộ cột tối thiểu nên khóa lại để cả `Solution 2` và `Solution 1` cùng dùng. `Solution 1` chỉ còn ý nghĩa baseline/historical reference:

- `property_id`
- `title`
- `district`
- `ward`
- `location_raw`
- `price_million_vnd`
- `price_billion_vnd`
- `area_m2`
- `price_per_m2_million`
- `bedrooms`
- `bathrooms`
- `floors`
- `latitude`
- `longitude`
- `description_snippet`
- `distance_to_nearest_school_m`
- `distance_to_nearest_park_m`
- `distance_to_nearest_hospital_m`
- `distance_to_nearest_supermarket_m`
- `distance_to_nearest_boulevard_m`

## 4. Thống kê nhanh

### 4.1. Dữ liệu bất động sản

- Giá: `1.25 - 27.0` tỷ VND, trung bình `8.27` tỷ
- Diện tích: `20.0 - 258.4` m², trung bình `69.1` m²
- Số phòng ngủ: `1 - 7`, trung bình `3.5`

### 4.2. Phân bố theo quận

- `Gò Vấp`: `50`
- `Tân Bình`: `50`

### 4.3. Một số phường xuất hiện nhiều

- `Phường Bảy Hiền`: `14`
- `Phường Gò Vấp`: `13`
- `Phường Thông Tây Hội`: `13`
- `Phường An Hội Tây`: `13`
- `Phường Tân Sơn`: `12`
- `Phường Tân Bình`: `10`

## 5. Vấn đề dữ liệu cần lưu ý

### 5.1. Cột có null hoặc thiếu dữ liệu

- `floors`: thiếu `2/100`
- `direction`: thiếu `75/100`
- `position`: thiếu `14/100`
- `description_snippet`: thiếu `5/100`
- toàn bộ `distance_to_nearest_*`: thiếu `100/100` vì bộ này chưa enrich

### 5.2. Đánh giá tác động

- `direction` không nên đưa vào scoring chính.
- `position` có thể giữ để mô tả, nhưng không nên là cột bắt buộc cho validation.
- `description_snippet` nên giữ nếu cần giải thích hoặc semantic search, nhưng pipeline cần chấp nhận giá trị rỗng.
- Các cột `distance_to_nearest_*` hiện chưa thể dùng cho ranking cho đến khi hoàn tất bước enrich.

### 5.3. Cột ổn định

Nhóm cột ổn định nhất hiện tại là:

- `property_id`
- `district`
- `ward`
- `price_million_vnd`
- `area_m2`
- `bedrooms`
- `bathrooms`
- `latitude`
- `longitude`

## 6. Khuyến nghị khóa schema

Nên khóa một quy ước chung:

- Đơn vị giá chính: `price_million_vnd`
- Đơn vị khoảng cách: mét
- Khóa định danh duy nhất: `property_id`
- Hard constraints mặc định: `budget_max_million`, `min_bedrooms`
- Soft preference tạm thời có thể dựa trên `area_m2` + `price_million_vnd`
- Nếu muốn dùng POI để ranking, cần enrich lại bộ `100` căn trước

## 7. Kết luận của member-3

Dataset `100` căn hiện tại đủ để:

- mở rộng quy mô dữ liệu cho nhóm
- chuẩn bị source chung cho giai đoạn final
- làm cơ sở cho bước enrich tiếp theo

Nhưng cần ghi rõ:

- đây là bộ clean dataset, chưa phải enriched dataset
- các cột `direction`, `position`, `description_snippet` chưa đồng đều
- các cột khoảng cách POI đang để `None`
- nếu muốn dùng ngay cho ranking giống pipeline cũ, cần enrich tiếp
