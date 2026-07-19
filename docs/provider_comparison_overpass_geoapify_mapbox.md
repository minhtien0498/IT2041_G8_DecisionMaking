# So sánh Overpass, Geoapify và Mapbox

Ngày cập nhật: `2026-07-16`

## Mục tiêu

Tài liệu này so sánh ba hướng enrich POI cho bộ `100` bất động sản ở Gò Vấp và Tân Bình:

- `Overpass API` của OpenStreetMap.
- `Geoapify Places API`.
- `Mapbox Tilequery API`.

Tên file đã được đổi thành `provider_comparison_overpass_geoapify_mapbox.md` để phản ánh đúng việc tài liệu hiện so sánh đủ cả 3 provider.

## Kết quả tổng quan

### Trạng thái output và vận hành

| Tiêu chí | Overpass | Geoapify | Mapbox |
|---|---:|---:|---:|
| Số record output hiện có | 100/100 | 100/100 | 100/100 |
| Số `property_id` duy nhất | 100 | 100 | 100 |
| Error log cuối | 0 lỗi | 0 lỗi | 0 lỗi |
| Thời gian chạy quan sát | 55 phút 25 giây | 16 phút 47 giây | 54.5 giây |
| Tình huống lỗi khi chạy | Có gặp 429/504, đã retry thành công | Không ghi nhận lỗi API | Không ghi nhận lỗi API |
| Độ ổn định khi chạy | Trung bình | Tốt | Tốt |
| Vai trò đề xuất | Baseline open-data | Baseline thương mại đối chiếu | Provider final cho workflow hiện tại |

### Phạm vi feature sinh ra

| Tiêu chí | Overpass | Geoapify | Mapbox |
|---|---|---|---|
| Số nhóm POI có field trong output | 7 | 7 | 10 |
| Số nhóm POI có dữ liệu thực tế | 7/7 | 7/7 | 9/10 |
| Nhóm chung với cả 3 provider | school, park, hospital, supermarket, market, cafe | school, park, hospital, supermarket, market, cafe | school, park, hospital, supermarket, market, cafe |
| Nhóm chỉ Overpass/Geoapify có trong schema hiện tại | boulevard | boulevard | Không có boulevard hữu dụng trong mapping hiện tại |
| Nhóm mở rộng Mapbox có thêm | Không có | Không có | kindergarten, pharmacy, gym |
| Nhóm có độ phủ nổi bật | school, cafe, boulevard | school, park, cafe, boulevard | school, supermarket, cafe, pharmacy |

### Metric raw result count

| Metric | Overpass | Geoapify | Mapbox |
|---|---|---|---|
| `api_result_count` trung bình | 206.18 | 121.69 | Không cùng schema |
| Ý nghĩa | Số OSM elements raw trả về sau 1 query/căn | Tổng places raw trả về sau các request category/căn | Script hiện chỉ lưu feature đã chuẩn hóa, không lưu tổng raw Tilequery features |

Không nên đọc `api_result_count` như một metric chất lượng trực tiếp. Con số này chỉ cho biết mỗi provider trả về bao nhiêu đối tượng raw trước khi nhóm lọc/map thành feature. Với Mapbox, output hiện tại không lưu tổng raw result count, nên phần này được ghi là `Không cùng schema` thay vì ép thành `0` hoặc một số không tương đương.

Ghi chú cập nhật:

- Overpass trước đó chỉ có `90/100` mẫu, thiếu `TB_041`--`TB_050`.
- Ngày `2026-07-16`, nhóm đã chạy resume bằng checkpoint và bổ sung đủ `TB_041`--`TB_050`.
- Trong lượt resume Overpass có gặp `429 Too Many Requests` và `504 Gateway Timeout`, nhưng script retry/cache/checkpoint đã hoàn tất đủ `100/100` và error log cuối là `0`.
- Mapbox đã có output `100/100` trong `data/mapbox/` và được nhóm chọn làm nguồn tiện ích final cho Solution 1 và Solution 2.

## 1. Giá cả và mô hình sử dụng

| Tiêu chí | Overpass | Geoapify | Mapbox |
|---|---|---|---|
| API key | Không cần với public instance | Bắt buộc | Bắt buộc |
| Chi phí cơ bản | Miễn phí nếu dùng public instance | Có free plan | Có free tier/usage quota theo tài khoản |
| Free tier | Không thu phí, nhưng quota động theo tải server | `3000 credits/day` | Phụ thuộc loại API và tài khoản Mapbox |
| Giới hạn tốc độ | Không có con số cố định; phụ thuộc slot, thời gian chạy query và tải server | Gói Free hiện tại `up to 5 requests/second` | Ổn định hơn public Overpass, nhưng vẫn cần quản lý quota/token |
| Cách tính chi phí | Không tính tiền, nhưng bị giới hạn tài nguyên công cộng | Tính theo credits và số places trả về | Tính theo request/usage của từng API |
| Phù hợp khi nào | Nghiên cứu, thử nghiệm, open-data, chi phí thấp | Benchmark thương mại, đối chiếu độ phủ | Demo/workflow final cần tốc độ và tích hợp Mapbox |

## 2. Tốc độ và thời gian chạy quan sát được

| Provider | Trạng thái test | Thời gian thực tế ghi nhận |
|---|---|---|
| Overpass | Đã chạy đủ `100` mẫu sau khi resume `TB_041`--`TB_050` | `55 phút 25 giây` cho lần full run trước; resume 10 mẫu ngày `2026-07-16` vẫn gặp 429/504 |
| Geoapify | Đã chạy đủ `100` mẫu | `16 phút 47 giây` cho `100` mẫu |
| Mapbox | Đã chạy đủ `100` mẫu | `54.5 giây` cho `100` mẫu |

### Overpass

- Dùng public instance nên bị ảnh hưởng mạnh bởi quota động.
- Khi chạy full/resume, có thể gặp:
  - `429 Too Many Requests`
  - `504 Gateway Timeout`
- Sau khi dùng `batch`, `checkpoint`, `cache`, `status check` và `retry`, pipeline có thể hoàn tất đủ dữ liệu.
- Phù hợp làm baseline open-data và chạy nền; không nên kỳ vọng chạy tươi toàn bộ 100 căn thật nhanh trong mọi thời điểm.

### Geoapify

- Chạy ổn định hơn Overpass trong các lần test hiện tại.
- Không phát sinh lỗi API trong error log.
- Phù hợp làm baseline thương mại để đối chiếu độ phủ POI và tính ổn định vận hành.

### Mapbox

- Chạy nhanh nhất trong test hiện tại: `100` mẫu trong khoảng `54.5` giây.
- Dùng chung được cho dataset-level enrichment và dynamic enrichment theo free-text.
- Được chọn làm provider final cho Solution 1 và Solution 2, trong khi Overpass/Geoapify giữ vai trò baseline đối chiếu.

## 3. Limit, quota và vận hành

### Overpass

- Endpoint chính: `https://overpass-api.de/api/interpreter`
- Public instance có quota động.
- Nên kiểm tra `https://overpass-api.de/api/status` trước khi gọi.
- Cần:
  - `batch`
  - `checkpoint`
  - `cache`
  - `retry`
  - `pause` giữa các batch

### Geoapify

- Endpoint chính: `https://api.geoapify.com/v2/places`
- Là API thương mại nên hành vi ổn định hơn public Overpass.
- Cần quản lý API key và kiểm soát số category, bán kính, `limit`.

### Mapbox

- Endpoint đang dùng trong repo: `Mapbox Tilequery API` trên tileset `mapbox.mapbox-streets-v8`.
- Script đọc token từ biến môi trường `MAPBOX_TOKEN`.
- Cần cache output để đảm bảo demo và validation tái lập.
- Không nên commit token vào repo.

## 4. Độ đầy dữ liệu

Số lượng giá trị `null` trên các trường khoảng cách ở output hiện tại:

| Field | Overpass null | Geoapify null | Mapbox null |
|---|---:|---:|---:|
| `distance_to_nearest_school_m` | 0 | 0 | 0 |
| `distance_to_nearest_park_m` | 0 | 0 | 23 |
| `distance_to_nearest_hospital_m` | 2 | 27 | 25 |
| `distance_to_nearest_supermarket_m` | 1 | 2 | 3 |
| `distance_to_nearest_market_m` | 1 | 3 | 24 |
| `distance_to_nearest_cafe_m` | 0 | 0 | 4 |
| `distance_to_nearest_boulevard_m` | 0 | 0 | 100 |
| `distance_to_nearest_kindergarten_m` | N/A | N/A | 63 |
| `distance_to_nearest_pharmacy_m` | N/A | N/A | 35 |
| `distance_to_nearest_gym_m` | N/A | N/A | 78 |

Số bất động sản có ít nhất một POI trong bán kính `1 km`:

| Nhóm POI | Overpass | Geoapify | Mapbox |
|---|---:|---:|---:|
| School | 100/100 | 100/100 | 100/100 |
| Park | 96/100 | 96/100 | 77/100 |
| Hospital/clinic | 73/100 | 52/100 | 75/100 |
| Supermarket | 78/100 | 78/100 | 97/100 |
| Market | 84/100 | 84/100 | 76/100 |
| Cafe | 100/100 | 99/100 | 96/100 |
| Boulevard | 100/100 | 100/100 | 0/100 |
| Kindergarten | N/A | N/A | 37/100 |
| Pharmacy | N/A | N/A | 65/100 |
| Gym | N/A | N/A | 22/100 |

Nhận xét:

- Overpass có độ phủ tốt ở `school`, `park`, `cafe`, `boulevard`; sau khi chạy đủ 100 mẫu, nhóm `hospital` chỉ thiếu 2 mẫu về khoảng cách gần nhất.
- Geoapify ổn định, nhưng mapping hiện tại thiếu nhiều ở nhóm `hospital`.
- Mapbox rất nhanh và có thêm các nhóm tiện ích hữu ích như `pharmacy`, `gym`, `kindergarten`; tuy nhiên mapping hiện tại chưa có `boulevard` và còn thiếu ở `kindergarten`, `gym`.
- Nếu cần đánh giá giao thông/trục đường lớn, Overpass hoặc Geoapify vẫn hữu ích để bổ sung/đối chiếu với Mapbox.

## 5. Độ ổn định

### Overpass

- Error log cuối là `0`, nhưng quá trình chạy thực tế vẫn gặp rate limit và gateway timeout.
- Điểm mạnh là nguồn mở và độ phủ tốt ở một số nhóm POI.
- Điểm yếu là thời gian chạy khó dự đoán.

### Geoapify

- Error log cuối là `0`.
- Chạy đủ `100` record, tốc độ tốt hơn Overpass.
- Phù hợp để so sánh với provider final hoặc dùng làm fallback thương mại.

### Mapbox

- Error log cuối là `0`.
- Chạy đủ `100` record nhanh nhất trong các provider hiện có.
- Phù hợp nhất với hướng nhóm đã chốt: Solution 1 và Solution 2 đều dùng Mapbox cho enrichment.

## 6. Kết luận nhanh

- Nếu ưu tiên `miễn phí / open-data`: dùng `Overpass`, nhưng phải chấp nhận chậm và cần `batch + cache + checkpoint`.
- Nếu ưu tiên `baseline thương mại để đối chiếu`: dùng `Geoapify`.
- Nếu ưu tiên `workflow final, tốc độ và tích hợp với Solution 1/2`: dùng `Mapbox`.
- Hướng hợp lý cho nhóm hiện tại:
  - dùng `Mapbox` làm provider final;
  - giữ `Overpass` làm baseline open-data;
  - giữ `Geoapify` làm baseline thương mại/fallback;
  - cache toàn bộ output để demo và validation không bị lệch do API thay đổi.

## 7. Tài liệu tham chiếu trong repo

- Overpass notebook: [notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb](../notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb)
- Geoapify notebook: [notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb](../notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb)
- Mapbox notebook: [notebooks/enrich_gv_tb_100_mapbox_pipeline.ipynb](../notebooks/enrich_gv_tb_100_mapbox_pipeline.ipynb)
- Overpass script: [src/data/enrich_gv_tb_100_overpass_api.py](../src/data/enrich_gv_tb_100_overpass_api.py)
- Mapbox script: [src/data/enrich_gv_tb_100_mapbox.py](../src/data/enrich_gv_tb_100_mapbox.py)
- Overpass schema: [data/overpass/overpass_enriched_schema_readme.json](../data/overpass/overpass_enriched_schema_readme.json)
- Geoapify schema: [data/geoapify/geoapify_enriched_schema_readme.json](../data/geoapify/geoapify_enriched_schema_readme.json)
- Mapbox schema: [data/mapbox/mapbox_enriched_schema_readme.json](../data/mapbox/mapbox_enriched_schema_readme.json)
- Overpass cURL: [data/overpass/overpass_api_curl_examples.md](../data/overpass/overpass_api_curl_examples.md)
- Geoapify cURL: [data/geoapify/geoapify_api_curl_examples.md](../data/geoapify/geoapify_api_curl_examples.md)
- Mapbox cURL: [data/mapbox/mapbox_api_curl_examples.md](../data/mapbox/mapbox_api_curl_examples.md)
