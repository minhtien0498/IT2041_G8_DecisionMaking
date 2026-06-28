# Ghi Chú Mở Rộng Dataset

## Mục tiêu

Tạo bộ dataset mới gồm `100` căn theo quota:

- `50` căn ở `Gò Vấp`
- `50` căn ở `Tân Bình`

## Kết quả đã tạo

Dataset mới đã được sinh:

- `data/go_vap_tan_binh_100.json`

Script extract đã được tạo:

- `src/data/prepare_gv_tb_100.py`

## Lưu ý

Hai file trên là file dùng chung cho nhóm, vì:

- Solution 1 và Solution 2 đều có thể dùng chung
- member-4 có thể cần để tạo validation set
- nhóm có thể cần dùng lại để enrich hoặc benchmark

Vì vậy, chúng **không được move vào thư mục riêng của member-3**.

## Trạng thái hiện tại

Dataset `go_vap_tan_binh_100.json` hiện là bộ clean dataset:

- có `property_id`
- có `price`, `area`, `bedrooms`, `bathrooms`
- có `lat/lon`
- chưa enrich lại các cột `distance_to_nearest_*`

Nếu cần sử dụng cho ranking có feature POI, cần làm thêm bước enrich cho bộ 100 căn này.
