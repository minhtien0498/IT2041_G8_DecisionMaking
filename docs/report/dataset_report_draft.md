# Bản Thô Báo Cáo - Dataset và Tiền Xử Lý Dữ Liệu

## 1. Tổng quan dataset

Phần việc của member-3 hiện tập trung vào bộ dữ liệu mở rộng `data/go_vap_tan_binh_100.json`. File này gồm `100` bất động sản dạng `Nhà riêng`, trong đó có `50` căn ở `Gò Vấp` và `50` căn ở `Tân Bình`. Ngoài ra, repo vẫn có hai nguồn lớn hơn để mở rộng trong giai đoạn sau: `data/raw/data_public.csv` với `51,304` dòng và `data/raw/vietnam_housing_dataset.csv` với `30,229` dòng.

Bộ dataset 100 căn được chọn nhằm tăng quy mô dữ liệu so với bản nhỏ trước đó và tạo tiền đề cho giai đoạn final. Mỗi bất động sản có `property_id` duy nhất, thông tin giá, diện tích, số phòng, vị trí, tọa độ. Tuy nhiên, bộ này hiện mới ở trạng thái `clean dataset`, chưa enrich lại các cột khoảng cách POI.

## 2. Schema dữ liệu được dùng trong project

Những cột được xem là cột nền để hai solution chính cùng dùng gồm:

- `property_id`, `title`, `district`, `ward`, `location_raw`
- `price_million_vnd`, `price_billion_vnd`, `area_m2`, `price_per_m2_million`
- `bedrooms`, `bathrooms`, `floors`
- `latitude`, `longitude`
- `description_snippet`
- `distance_to_nearest_school_m`
- `distance_to_nearest_park_m`
- `distance_to_nearest_hospital_m`
- `distance_to_nearest_supermarket_m`
- `distance_to_nearest_boulevard_m`

Việc khóa bộ cột này giúp `Solution 2` và `Solution 1` chạy trên cùng một nguồn thông tin. Với Solution 1, các cột này là nhóm tiện ích nền `X`; nếu free-text yêu cầu tiện ích ngoài nhóm này thì pipeline có thể enrich thêm nhóm thuộc tính động `Y`. Tuy nhiên, ở bộ 100 căn clean ban đầu, các cột khoảng cách POI vẫn đang là `None`, nên nếu muốn dùng cho ranking có POI thì cần enrich tiếp.

## 3. Thống kê nhanh

Trong `data/go_vap_tan_binh_100.json`, giá bất động sản nằm trong khoảng `1.25 - 27.0` tỷ VND, trung bình `8.27` tỷ. Diện tích nằm trong khoảng `20.0 - 258.4` m², trung bình `69.1` m². Số phòng ngủ dao động từ `1` đến `7`, trung bình `3.5`.

Về phân bố địa lý, dữ liệu hiện được chia đều:

- Gò Vấp: `50` mẫu
- Tân Bình: `50` mẫu

Một số phường xuất hiện nhiều gồm:

- Phường Bảy Hiền: `14`
- Phường Gò Vấp: `13`
- Phường Thông Tây Hội: `13`
- Phường An Hội Tây: `13`

## 4. Ghi chú tiền xử lý dữ liệu

Quá trình rà soát cho thấy dataset đã đạt mức ổn định cơ bản ở lớp dữ liệu clean, nhưng vẫn có một số cột cần lưu ý:

- `floors` thiếu `2/100`
- `direction` thiếu `75/100`
- `position` thiếu `14/100`
- `description_snippet` thiếu `5/100`
- toàn bộ các cột `distance_to_nearest_*` đang thiếu `100/100`

Do mức độ thiếu lớn, `direction` không nên đưa vào scoring chính. `position` và `description_snippet` có thể giữ lại cho mô tả hoặc semantic support, nhưng pipeline phải chấp nhận giá trị rỗng. Quan trọng hơn, bộ 100 căn hiện chưa enrich POI nên chưa thể dùng ngay cho ranking có dựa trên khoảng cách đến trường học, công viên, bệnh viện hay siêu thị.

## 5. Vì sao dataset này phù hợp cho giai đoạn hiện tại

Dataset hiện tại phù hợp cho mục tiêu mở rộng dữ liệu vì:

1. Hai solution chính có thể chạy trên cùng một bộ dữ liệu.
2. Schema đã rõ ràng và có thể dùng làm chuẩn chung.
3. Bộ này giúp nhóm tiến gần hơn tới target khoảng `100` nhà thay vì chỉ dùng bản nhỏ.

Tuy nhiên, nhóm cần ghi rõ trong báo cáo rằng đây là bộ `clean dataset`, chưa phải bộ `enriched dataset`. Nếu cần dùng cho ranking đầy đủ ở bản final, cần thực hiện tiếp bước enrichment cho các cột POI, sau đó mới chạy evaluation trên bộ 100 căn này.

## 6. Ghi chú bàn giao

Phần này là `report thô` của member-3. Khi ghép final report, cần giữ thống nhất các tên trường và đơn vị với:

- output contract của member-4
- validation set chung
- phần mô tả `Solution 2` và `Solution 1`
