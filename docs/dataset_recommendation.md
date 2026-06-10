# Dataset Recommendation V2 - Smart Real Estate Advisory System

File này là phương án dataset mới nếu nhóm muốn chuyển từ hướng fact-checking sang đề tài **Hệ thống tư vấn chọn bất động sản thông minh**.

Checklist chuẩn bị API, lọc data gốc và fallback giữa 2 phương án nằm ở:

```text
docs/datasets/real_estate_data_preparation_plan.md
```

## 1. Problem Fit

Đề tài BĐS phù hợp trực tiếp với môn Hệ hỗ trợ ra quyết định vì output là:

```text
User preference -> Scoring/Ranking -> Top 3 recommended properties -> Explanation
```

Hệ thống không chỉ dự đoán giá, mà hỗ trợ người dùng chọn BĐS phù hợp với tài chính, nhu cầu gia đình, vị trí, tiện ích và mức độ ưu tiên cá nhân.

## 2. Recommended Dataset Pair

Phương án nên ưu tiên:

```text
Real Estate Listings + POI/Amenity Data
```

| Source | Dataset | Vai trò | Link |
|---|---|---|---|
| Source 1 | Ho Chi Minh City Real Estate Data 2025 | Dữ liệu BĐS chính: giá, diện tích, vị trí, mô tả, thuộc tính căn hộ/nhà | https://www.kaggle.com/datasets/cnglmph/ho-chi-minh-city-real-estate-data-2025 |
| Source 1 alternative | House Price Prediction Dataset Vietnam 2024 | Dữ liệu BĐS Việt Nam crawl từ batdongsan.vn, có address, area, bedrooms, bathrooms, floors, price | https://www.kaggle.com/datasets/nguyentiennhan/vietnam-housing-dataset-2024 |
| Source 2 | OpenStreetMap POI / Geofabrik / OpenStreetData | Dữ liệu tiện ích xung quanh: trường học, bệnh viện, công viên, siêu thị, giao thông | https://download.geofabrik.de/ ; https://openstreetdata.org/ |
| Optional | GADM / Vietnam administrative boundaries | Chuẩn hóa vị trí theo tỉnh, quận/huyện, phường/xã | https://gadm.org/ |

## 3. Why These Two Data Sources?

### Source 1: Real Estate Listings

Dùng để mô tả bản thân BĐS:

- Giá.
- Diện tích.
- Số phòng ngủ / phòng tắm.
- Vị trí / địa chỉ.
- Loại BĐS.
- Tình trạng nội thất / pháp lý nếu có.
- Mô tả text nếu dataset cung cấp.

Đây là dataset lõi để hệ thống recommend Top 3 căn phù hợp.

### Source 2: POI / Amenities

Dùng để tạo attribute quyết định:

- Gần trường học.
- Gần bệnh viện.
- Gần công viên.
- Gần siêu thị.
- Gần khu công nghiệp.
- Gần trạm xe bus / metro.
- Mật độ tiện ích trong bán kính 500m, 1km, 2km.

Đây là phần làm đề tài giống DSS hơn vì hệ thống biến dữ liệu vị trí thô thành tiêu chí ra quyết định.

## 4. Dataset Options

| Dataset | Nhóm dữ liệu | Input chính | Output/Label | Ưu điểm | Nhược điểm | Mức độ phù hợp |
|---|---|---|---|---|---|---|
| Ho Chi Minh City Real Estate Data 2025 | BĐS Việt Nam | Listing BĐS TP.HCM | Giá / thuộc tính listing | Sát bối cảnh Việt Nam, dễ kể chuyện tư vấn căn hộ | Có thể cần kiểm tra license và chất lượng cột | Rất cao |
| House Price Prediction Dataset Vietnam 2024 | BĐS Việt Nam | Address, area, bedrooms, bathrooms, floors, price | Price | Crawl từ batdongsan.vn, nhiều thuộc tính thực tế | Có thể thiếu tọa độ lat/lon, cần geocode hoặc xử lý district/ward | Rất cao |
| Vietnam Housing Dataset Hanoi | BĐS Hà Nội | Listing nhà đất Hà Nội | Price | Có thể dùng làm so sánh vùng miền | Cũ hơn, ít mô tả hơn | Trung bình-cao |
| OpenStreetMap POI | Tiện ích đô thị | POI tags, lat/lon, category | Amenity features | Open, linh hoạt, đúng nhu cầu tạo attribute | Cần xử lý GIS/khoảng cách; dữ liệu có thể thiếu/không đồng đều | Rất cao |
| OpenStreetData | Address/POI extract | Address, street, POI, geocoordinate | Amenity/location features | Dễ dùng hơn raw OSM trong vài trường hợp | Coverage tùy khu vực | Cao |
| GADM Vietnam | Ranh giới hành chính | Boundary polygons | Location grouping | Hữu ích để group theo quận/phường | Không có tiện ích hay giá | Phụ trợ |

## 5. Proposed Data Schema

Sau khi chuẩn hóa, mỗi BĐS nên có schema:

```json
{
  "property_id": "hcm_001",
  "title": "Apartment for sale in District 7",
  "price_vnd": 3500000000,
  "area_m2": 72,
  "bedrooms": 2,
  "bathrooms": 2,
  "district": "District 7",
  "ward": "Tan Phu",
  "address": "District 7, Ho Chi Minh City",
  "latitude": 10.729,
  "longitude": 106.721,
  "description": "Near school, park, shopping mall...",
  "legal_status": "pink book",
  "furnishing": "semi-furnished",
  "near_school_count_1km": 4,
  "near_park_count_1km": 2,
  "near_hospital_count_2km": 1,
  "near_supermarket_count_1km": 3,
  "distance_to_nearest_school_m": 350,
  "distance_to_nearest_park_m": 600,
  "affordability_score": 0.82,
  "family_score": 0.76,
  "convenience_score": 0.88,
  "investment_score": 0.64,
  "final_score": 0.79
}
```

## 6. Attribute Engineering

### Raw listing attributes

| Attribute | Meaning |
|---|---|
| `price_vnd` | Giá BĐS |
| `area_m2` | Diện tích |
| `price_per_m2` | Giá trên mỗi m2 |
| `bedrooms` | Số phòng ngủ |
| `bathrooms` | Số phòng tắm |
| `district`, `ward` | Khu vực |
| `legal_status` | Pháp lý nếu có |
| `furnishing` | Tình trạng nội thất |

### Derived amenity attributes

| Attribute | Meaning |
|---|---|
| `near_school_count_1km` | Số trường học trong bán kính 1km |
| `near_park_count_1km` | Số công viên trong bán kính 1km |
| `near_hospital_count_2km` | Số bệnh viện trong bán kính 2km |
| `near_supermarket_count_1km` | Số siêu thị/cửa hàng trong bán kính 1km |
| `distance_to_nearest_school_m` | Khoảng cách đến trường gần nhất |
| `distance_to_nearest_park_m` | Khoảng cách đến công viên gần nhất |

### Decision scores

| Score | Example logic |
|---|---|
| `affordability_score` | Giá nằm trong ngân sách user, giá/m2 hợp lý |
| `family_score` | Gần trường học, công viên, bệnh viện; đủ phòng ngủ |
| `convenience_score` | Gần siêu thị, giao thông, tiện ích |
| `investment_score` | Khu vực tăng trưởng, giá/m2 cạnh tranh |
| `final_score` | Weighted sum theo preference của user |

## 7. User Preference Extraction

LLM có thể đọc input người dùng và trích xuất preference:

Input example:

```text
Tôi có gia đình 4 người, có 2 con nhỏ, muốn mua căn hộ dưới 4 tỷ, ưu tiên gần trường học và công viên, không quá xa trung tâm.
```

Parsed preference:

```json
{
  "budget_max_vnd": 4000000000,
  "family_with_children": true,
  "min_bedrooms": 2,
  "preferred_amenities": ["school", "park"],
  "location_priority": "near_center",
  "weights": {
    "affordability_score": 0.35,
    "family_score": 0.35,
    "convenience_score": 0.20,
    "investment_score": 0.10
  }
}
```

## 8. Recommendation Pipeline

```text
Raw BĐS listings
        |
        v
Clean + normalize price/area/location
        |
        v
Join with POI / amenities data
        |
        v
Generate derived attributes
        |
        v
User input
        |
        v
LLM extracts user preferences
        |
        v
Rule-based / content-based scoring
        |
        v
Top 3 properties
        |
        v
LLM explains recommendation
```

## 9. Two Possible Solutions

### Solution 1: Rule-Based / Weighted Scoring

- User điền form tiêu chí.
- Hệ thống gán trọng số thủ công.
- Tính điểm từng BĐS theo weighted sum.
- Trả về Top 3.

Ưu điểm:

- Dễ làm.
- Minh bạch.
- Dễ giải thích trong DSS.

Nhược điểm:

- Ít linh hoạt.
- Phụ thuộc vào trọng số nhóm tự thiết kế.

### Solution 2: LLM-Assisted Preference Extraction + Explanation

- User nhập nhu cầu bằng ngôn ngữ tự nhiên.
- LLM trích xuất preference và trọng số.
- Scoring engine tính Top 3.
- LLM sinh giải thích vì sao hệ thống gợi ý các căn đó.

Ưu điểm:

- Gần trải nghiệm tư vấn thật.
- Dễ demo.
- Phù hợp yêu cầu có LLM.

Nhược điểm:

- Cần kiểm soát hallucination.
- LLM không nên tự bịa dữ liệu BĐS; chỉ giải thích dựa trên attribute đã tính.

## 10. EDA Plan

EDA cơ bản cần có:

| EDA item | Metric |
|---|---|
| Dataset size | Số listing |
| Price distribution | Min, max, mean, median price |
| Area distribution | Min, max, mean, median area |
| Price per m2 | Mean/median by district |
| Location distribution | Số listing theo district/ward |
| Bedrooms/bathrooms | Phân phối số phòng |
| Missing values | Thiếu giá, diện tích, vị trí |
| Amenity coverage | Tỷ lệ listing có POI trong bán kính 1km |
| Derived score distribution | family/convenience/affordability score |

Chart nên có:

- Bar chart: số listing theo district.
- Histogram: price.
- Histogram: area.
- Boxplot: price per m2 by district.
- Bar chart: số POI trung bình quanh mỗi listing.
- Scatter: price vs area.

## 11. Evaluation Plan

Vì đây là recommender system, không nên chỉ dùng accuracy.

| Evaluation | Meaning |
|---|---|
| Top-K relevance | Top 3 có phù hợp preference không |
| Constraint satisfaction | Có vi phạm budget, số phòng, vị trí không |
| Score explainability | Điểm số có giải thích được không |
| Rule consistency | Cùng input thì ranking có ổn định không |
| User-case testing | Test bằng 5-10 persona khác nhau |
| LLM explanation quality | Giải thích có dựa đúng attribute không |

Ví dụ persona test:

- Gia đình có con nhỏ: ưu tiên trường học, công viên, bệnh viện.
- Người độc thân: ưu tiên gần trung tâm, tiện ích, giao thông.
- Nhà đầu tư: ưu tiên giá/m2 thấp, khu vực tăng trưởng.
- Người cao tuổi: ưu tiên bệnh viện, yên tĩnh, tầng thấp.

## 12. Risks

| Risk | Mitigation |
|---|---|
| Dataset thiếu lat/lon | Dùng district/ward-level scoring hoặc geocode một phần |
| POI data không đầy đủ | Chỉ dùng vài loại POI dễ có: school, hospital, park, supermarket |
| Listing price không phải transaction price | Ghi rõ đây là listing/ad price, không phải giá giao dịch cuối |
| Trọng số scoring chủ quan | Nêu rõ là rule-based baseline; Solution 2 dùng LLM để cá nhân hóa trọng số |
| LLM hallucinate | Bắt LLM chỉ giải thích dựa trên fields đã tính |

## 13. Recommendation

Nếu nhóm quyết định đổi đề tài, nên chọn:

```text
Ho Chi Minh City Real Estate Data 2025 + OpenStreetMap POI
```

Lý do:

- Sát bối cảnh Việt Nam.
- Dễ giải thích theo DSS.
- Có đủ đất cho EDA, feature engineering, scoring, recommendation, và LLM explanation.
- Đáp ứng yêu cầu 2 nguồn dữ liệu: một nguồn BĐS, một nguồn tiện ích/vị trí.

Nếu dataset HCMC thiếu field quan trọng, fallback:

```text
House Price Prediction Dataset Vietnam 2024 + OpenStreetMap POI
```
