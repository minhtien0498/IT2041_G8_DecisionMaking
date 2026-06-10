# Real Estate Data Preparation Plan

File này chuẩn bị thông tin cần thiết cho 2 phương án dataset của đề tài **Hệ thống tư vấn chọn bất động sản thông minh**.

## 1. Hai phương án trình bày với thầy

### Phương án 2 - Ưu tiên show trước

```text
1 dataset BĐS + 1 dataset tiện ích xung quanh
```

Ví dụ:

```text
Ho Chi Minh City Real Estate Data 2025
+ OpenStreetMap / Mapbox / Google Maps POI
```

Ý nghĩa:

- Dataset BĐS cung cấp thông tin căn hộ/nhà: giá, diện tích, vị trí, mô tả.
- Dataset tiện ích xung quanh tạo thêm attribute DSS: gần trường học, công viên, bệnh viện, siêu thị, khu công nghiệp.
- Đây là phương án đúng tinh thần DSS hơn vì hệ thống biến dữ liệu thô thành tiêu chí ra quyết định.

### Phương án 1 - Fallback nếu phương án 2 không kịp

```text
2 dataset BĐS từ Kaggle
```

Ví dụ:

```text
Ho Chi Minh City Real Estate Data 2025
+ House Price Prediction Dataset Vietnam 2024
```

Ý nghĩa:

- Dễ làm hơn vì chỉ cần xử lý 2 file listing BĐS.
- Có thể so sánh 2 nguồn / 2 năm / 2 schema.
- Yếu hơn phương án 2 ở phần DSS vì thiếu dữ liệu tiện ích xung quanh.

## 2. Dataset chính cần chuẩn bị

| Dataset | Link | Cần kiểm tra |
|---|---|---|
| Ho Chi Minh City Real Estate Data 2025 | https://www.kaggle.com/datasets/cnglmph/ho-chi-minh-city-real-estate-data-2025 | Có cột giá, diện tích, địa chỉ/quận, loại BĐS, mô tả, lat/lon không |
| House Price Prediction Dataset Vietnam 2024 | https://www.kaggle.com/datasets/nguyentiennhan/vietnam-housing-dataset-2024 | Có address, area, bedrooms, bathrooms, floors, price; có thiếu lat/lon không |
| OpenStreetMap Vietnam | https://download.geofabrik.de/asia/vietnam.html | Tải `.osm.pbf` hoặc shapefile; lọc POI theo tags |
| Mapbox | https://docs.mapbox.com/api/search/geocoding/ | Cần access token; dùng geocoding hoặc search/POI nếu cần |
| Google Maps Platform | https://developers.google.com/places/web-service/search | Cần API key + billing; dùng Geocoding API hoặc Places Nearby Search |

## 3. Thông tin cần bổ sung trước khi code

### Từ dataset BĐS

Cần mở file Kaggle và ghi lại:

| Câu hỏi | Vì sao cần |
|---|---|
| File format là CSV, Excel hay JSON? | Để viết loader |
| Có bao nhiêu rows? | Để báo cáo EDA |
| Cột giá tên gì? Đơn vị VND hay tỷ? | Để normalize `price_vnd` |
| Cột diện tích tên gì? Có đơn vị m2 không? | Để normalize `area_m2` |
| Có lat/lon không? | Nếu không có phải geocode |
| Có địa chỉ đầy đủ không? | Cần cho Mapbox/Google geocoding |
| Có quận/huyện/phường không? | Nếu không geocode được thì dùng scoring theo district |
| Có mô tả text không? | LLM có thể đọc mô tả để extract tiện ích/pháp lý |
| Có loại BĐS không? | Căn hộ, nhà phố, đất nền cần scoring khác nhau |
| Có số phòng ngủ/phòng tắm không? | Dùng cho family score |
| Missing value nhiều không? | Quyết định lọc hoặc fill |

### Từ POI / tiện ích

Cần quyết định:

| Câu hỏi | Gợi ý |
|---|---|
| Lấy tiện ích nào? | school, park, hospital, supermarket, bus stop, industrial area |
| Bán kính tính điểm? | 500m, 1km, 2km |
| Dùng khoảng cách gần nhất hay số lượng POI? | Nên dùng cả hai nếu kịp |
| Dùng OSM offline hay API online? | OSM offline ổn định hơn; Mapbox/Google tiện hơn nhưng cần key |
| Nếu listing không có lat/lon thì làm gì? | Geocode bằng Mapbox/Google hoặc dùng district-level fallback |

## 4. API / token cần chuẩn bị

Không commit API key vào Git. Nên dùng biến môi trường:

```bash
export MAPBOX_ACCESS_TOKEN="..."
export GOOGLE_MAPS_API_KEY="..."
```

Nếu làm file `.env`, không commit file đó.

```text
.env
```

Nên thêm vào `.gitignore` nếu project chưa có:

```text
.env
```

### Mapbox

Cần:

```text
MAPBOX_ACCESS_TOKEN
```

API có thể dùng:

| API | Dùng để làm gì |
|---|---|
| Geocoding API | Chuyển address -> lat/lon |
| Reverse Geocoding | Chuyển lat/lon -> địa chỉ/khu vực |
| Search Box / POI Search | Tìm POI xung quanh nếu không dùng OSM offline |

Ghi chú:

- Mapbox Geocoding API yêu cầu `access_token`.
- Geocoding API v6 không còn cung cấp POI data như v5; nếu cần POI thì xem Search Box API hoặc dùng OSM offline.
- Mapbox có rate limit theo API; Geocoding API được docs liệt kê 1000 requests/minute.

### Google Maps

Cần:

```text
GOOGLE_MAPS_API_KEY
```

API có thể dùng:

| API | Dùng để làm gì |
|---|---|
| Geocoding API | Chuyển address -> lat/lon |
| Places API Nearby Search | Tìm school, hospital, park, supermarket quanh lat/lon |
| Places Details API | Lấy thông tin chi tiết nếu cần |
| Maps JavaScript API | Chỉ cần nếu demo web map |

Ghi chú an toàn:

- Google Maps Platform nên bật billing.
- API key phải restrict theo API và theo app/IP/referrer.
- Không dùng chung key frontend và backend.
- Nên đặt quota thấp khi thử nghiệm để tránh phát sinh chi phí.

### OpenStreetMap / Geofabrik

Cần tải:

```text
vietnam-latest.osm.pbf
```

hoặc shapefile nếu muốn dễ đọc GIS hơn.

Ưu điểm:

- Không cần API key.
- Có thể xử lý offline.
- Hợp với coursework vì tránh rủi ro billing.

Nhược điểm:

- Cần biết lọc tag OSM.
- Cần tool đọc `.osm.pbf` hoặc shapefile.

## 5. Cách lọc data từ dataset BĐS gốc

### Step 1: Chọn loại BĐS

Nếu dataset có nhiều loại, nên lọc một scope rõ:

```text
apartment / condo / căn hộ
```

hoặc:

```text
nhà ở / house
```

Không nên trộn quá nhiều loại nếu scoring chưa đủ tốt.

### Step 2: Lọc giá và diện tích hợp lệ

Loại các dòng:

- Thiếu giá.
- Thiếu diện tích.
- Giá <= 0.
- Diện tích <= 0.
- Giá hoặc diện tích quá bất thường.

Gợi ý:

```text
area_m2 between 20 and 300
price_vnd between 500,000,000 and 50,000,000,000
```

Ngưỡng cụ thể điều chỉnh sau khi EDA.

### Step 3: Chuẩn hóa giá

Các dataset Việt Nam có thể ghi:

```text
3.5 tỷ
3500 triệu
3,500,000,000
35 triệu/m2
```

Cần convert về:

```text
price_vnd
price_per_m2
```

### Step 4: Chuẩn hóa địa chỉ

Cần tạo các cột:

```text
address_clean
district
ward
city
latitude
longitude
```

Nếu không có `latitude/longitude`:

- Ưu tiên geocode bằng Mapbox hoặc Google.
- Nếu API hạn chế, chỉ geocode 100-200 mẫu demo.
- Nếu không geocode được, dùng district-level scoring.

### Step 5: Deduplicate

Loại listing trùng bằng:

```text
title + address + area + price
```

hoặc fuzzy matching nếu cần.

### Step 6: Chọn subset demo

Cho midterm, chỉ cần:

```text
100-200 listing sạch
```

Ưu tiên đủ đa dạng:

- Nhiều quận.
- Nhiều mức giá.
- Nhiều diện tích.
- Có đủ lat/lon hoặc district.

## 6. Cách lọc POI từ OpenStreetMap

Các tag nên lấy:

| Nhóm tiện ích | OSM tags gợi ý |
|---|---|
| Trường học | `amenity=school`, `amenity=kindergarten`, `amenity=university`, `amenity=college` |
| Bệnh viện/y tế | `amenity=hospital`, `amenity=clinic`, `amenity=doctors`, `amenity=pharmacy` |
| Công viên/cây xanh | `leisure=park`, `landuse=grass`, `natural=wood` |
| Mua sắm | `shop=supermarket`, `shop=convenience`, `amenity=marketplace` |
| Giao thông | `highway=bus_stop`, `railway=station`, `public_transport=station` |
| Khu công nghiệp | `landuse=industrial`, `man_made=works` |

Output POI nên chuẩn hóa:

```json
{
  "poi_id": "osm_123",
  "name": "Truong THCS ...",
  "category": "school",
  "latitude": 10.75,
  "longitude": 106.67,
  "source": "osm",
  "raw_tag": "amenity=school"
}
```

## 7. Cách tạo attribute tiện ích

Với mỗi BĐS có `latitude/longitude`, tính:

```text
near_school_count_500m
near_school_count_1km
near_park_count_1km
near_hospital_count_2km
near_supermarket_count_1km
distance_to_nearest_school_m
distance_to_nearest_park_m
distance_to_nearest_hospital_m
distance_to_nearest_supermarket_m
```

Gợi ý bán kính:

| Attribute | Radius |
|---|---:|
| school | 1km |
| park | 1km |
| hospital | 2km |
| supermarket | 1km |
| bus/metro | 800m |
| industrial area | 3-5km |

## 8. Scoring gợi ý

### Affordability score

```text
Nếu price <= budget: score cao
Nếu price > budget: giảm mạnh theo mức vượt budget
```

### Family score

Tăng điểm nếu:

- Có ít nhất 2 phòng ngủ.
- Gần trường học.
- Gần công viên.
- Gần bệnh viện.
- Khu vực có nhiều tiện ích.

### Convenience score

Tăng điểm nếu:

- Gần siêu thị.
- Gần trạm xe bus/metro.
- Gần trung tâm hoặc khu việc làm.

### Investment score

Tăng điểm nếu:

- Giá/m2 thấp hơn median cùng quận.
- Khu vực có nhiều tiện ích.
- Diện tích và giá phù hợp thanh khoản.

## 9. Thông tin cần hỏi nhóm trước khi chốt

1. Nhóm chọn dataset BĐS chính là HCMC 2025 hay Vietnam Housing 2024?
2. Có cần tải cả 2 dataset Kaggle ngay không?
3. Có lat/lon trong dataset không?
4. Nhóm dùng Mapbox hay Google Maps để geocode?
5. Có chấp nhận chỉ geocode 100-200 mẫu để demo không?
6. Có dùng OSM offline làm nguồn POI chính không?
7. Nếu API hết quota, fallback sang phương án 1 như thế nào?
8. Sản phẩm demo là notebook, CLI hay web form?

## 10. File output nên tạo

```text
data/raw/real_estate/hcm_2025/
data/raw/real_estate/vietnam_housing_2024/
data/raw/poi/osm/

data/processed/real_estate/properties_clean.csv
data/processed/real_estate/poi_clean.csv
data/processed/real_estate/properties_with_amenities.csv
data/processed/real_estate/recommendation_subset_200.csv
```

## 11. Decision for slide

Nên trình bày với thầy theo thứ tự:

1. **Phương án 2**: 1 dataset BĐS + tiện ích xung quanh.
   - Đây là hướng chính.
   - DSS rõ hơn.
   - Có feature engineering và recommendation thật.

2. **Phương án 1**: 2 dataset BĐS Kaggle.
   - Là fallback.
   - Dễ hoàn thành nếu API/POI không kịp.

## 12. Sources

- Ho Chi Minh City Real Estate Data 2025: https://www.kaggle.com/datasets/cnglmph/ho-chi-minh-city-real-estate-data-2025
- House Price Prediction Dataset Vietnam 2024: https://www.kaggle.com/datasets/nguyentiennhan/vietnam-housing-dataset-2024
- Geofabrik Vietnam OpenStreetMap download: https://download.geofabrik.de/asia/vietnam.html
- Mapbox Geocoding API: https://docs.mapbox.com/api/search/geocoding/
- Mapbox API rate limits: https://docs.mapbox.com/api/guides/
- Google Places API Nearby Search: https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places/searchNearby
- Google Maps API key security guidance: https://developers.google.com/maps/api-security-best-practices

