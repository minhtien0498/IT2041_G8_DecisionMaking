# Mapbox API cURL examples

Các ví dụ dưới đây dùng biến môi trường `MAPBOX_TOKEN`.

```bash
export MAPBOX_TOKEN="your_mapbox_public_token_here"
```

## 1. Tilequery POI quanh một tọa độ

Ví dụ query POI trong bán kính 1 km quanh một tọa độ ở TP.HCM:

```bash
curl "https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/106.6575,10.8345.json?radius=1000&layers=poi_label&limit=50&access_token=${MAPBOX_TOKEN}"
```

Trong pipeline của nhóm, response từ Tilequery được lọc tiếp theo nhóm tiện ích như `school`, `park`, `hospital`, `supermarket`, `market`, `cafe`, `pharmacy`, `gym`.

## 2. Geocoding một địa điểm cụ thể

Ví dụ tìm tọa độ một địa điểm cụ thể để tính khoảng cách đến từng BĐS:

```bash
curl "https://api.mapbox.com/geocoding/v5/mapbox.places/Landmark%2081%20TP.HCM.json?limit=1&country=vn&language=vi&proximity=106.68,10.83&access_token=${MAPBOX_TOKEN}"
```

API geocoding này đang được dùng trong Solution 1 cho nhu cầu kiểu: “gần chỗ làm ở ...”, “gần Landmark 81”, hoặc một địa chỉ cụ thể do người dùng nhập.

## 3. Chạy pipeline enrich 100 BĐS bằng Mapbox

```bash
python3 src/data/enrich_gv_tb_100_mapbox.py
```

Smoke test 3 mẫu đầu:

```bash
python3 src/data/enrich_gv_tb_100_mapbox.py --max-records 3
```

Output chính:

- `data/mapbox/go_vap_tan_binh_100_enriched_mapbox_api.json`
- `data/mapbox/go_vap_tan_binh_100_enriched_mapbox_api_checkpoint.json`
- `data/mapbox/go_vap_tan_binh_100_mapbox_errors.json`
