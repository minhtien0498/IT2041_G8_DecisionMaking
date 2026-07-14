# So Sánh Overpass vs Geoapify

Ngày tổng hợp: `2026-07-11`

## Mục tiêu

So sánh nhanh hai hướng enrich POI cho bộ `100` bất động sản ở Gò Vấp và Tân Bình:

- `Overpass API` của OpenStreetMap
- `Geoapify Places API`

## Kết quả tổng quan

| Tiêu chí | Overpass | Geoapify |
|---|---:|---:|
| Số record output hiện có | 90 | 100 |
| Error log | 0 | 0 |
| `api_result_count` trung bình | 200.74 | 121.69 |
| Ấn tượng tốc độ thực tế | Chậm hơn, dễ bị quota/rate limit | Nhanh hơn, ổn định hơn |
| Độ ổn định khi chạy notebook | Trung bình | Tốt |

## 1. Giá cả và mô hình sử dụng

| Tiêu chí | Overpass | Geoapify |
|---|---|---|
| API key | Không cần với public instance | Bắt buộc |
| Chi phí cơ bản | Miễn phí nếu dùng public instance | Có free plan |
| Free tier | Không thu phí, nhưng quota động theo tải server | `3000 credits/day` |
| Giới hạn tốc độ | Không có con số cố định; phụ thuộc slot, thời gian chạy query và tải hệ thống | Gói Free hiện tại `up to 5 requests/second` |
| Cách tính chi phí | Không tính tiền, nhưng bị giới hạn tài nguyên công cộng | `1 credit` cho mỗi `20` places trả về |
| Phù hợp khi nào | Nghiên cứu, thử nghiệm, open-data, chi phí thấp | Demo ổn định hơn, benchmark thương mại, kiểm soát tốt hơn |

Ghi chú:

- `Overpass` là public infrastructure nên không có SLA thương mại.
- Theo tài liệu chính thức, public Overpass phù hợp cho nhu cầu nhỏ; có guideline khoảng `10.000 queries/day` và dưới `1 GB/day`, nhưng quota thực tế vẫn phụ thuộc trạng thái server.
- Với `Geoapify`, chi phí thực sự phụ thuộc số kết quả trả về ở từng category, nên cần kiểm soát `limit` và số lượng request/căn.

## 2. Tốc độ và thời gian chạy quan sát được

| Provider | Trạng thái test hôm nay | Thời gian thực tế ghi nhận |
|---|---|---|
| Overpass | Đã chạy đủ `100` mẫu trong phiên test | `55 phút 25 giây` cho `100` mẫu (theo timestamp file ngày `2026-07-11`) |
| Geoapify | Đã chạy đủ `100` mẫu | `16 phút 47 giây` cho `100` mẫu (theo timestamp file ngày `2026-07-11`) |

### Ghi chú về cách đọc thời gian

- Các mốc dưới đây là thời gian **quan sát thực tế trong ngày `2026-07-11`** khi nhóm chạy notebook và theo dõi checkpoint.
- Với `Geoapify`, nhóm đã có một lần chạy đủ `100` mẫu trong notebook hiện tại.
- Với `Overpass`, nhóm ghi nhận một lần chạy đủ `100` mẫu trong cùng điều kiện test để phục vụ báo cáo.

### Overpass

- Dùng public instance nên bị ảnh hưởng mạnh bởi quota động.
- Khi chạy full batch, đã từng gặp `429 Too Many Requests` và `504 Gateway Timeout`.
- Sau khi thêm `batch`, `checkpoint`, `status check` và `retry`, notebook chạy được ổn hơn nhưng vẫn chậm.
- Trong quá trình test thực tế, tốc độ tăng checkpoint không đều vì phụ thuộc slot của server công cộng.
- Overpass phù hợp hơn cho chạy nền, cache dần, hơn là kỳ vọng chạy tươi toàn bộ 100 căn thật nhanh.
- Quan sát thực tế hôm nay:
  - notebook đã chạy đủ `100` mẫu trong ngày `2026-07-11`
  - theo timestamp của file checkpoint, thời gian ghi nhận cho `100` mẫu là **55 phút 25 giây** (`16:45:36` -> `17:41:01`)
  - đây vẫn chưa phải benchmark ổn định tuyệt đối vì chỉ cần gặp thêm `429` hoặc `504` thì thời gian có thể đội lên đáng kể
- Cách ghi an toàn trong báo cáo:
  - `Trong phiên test ngày 2026-07-11, Overpass đã chạy đủ 100 mẫu trong 55 phút 25 giây. Thời gian thực tế vẫn phụ thuộc mạnh vào quota động và có thể tăng đáng kể khi gặp rate limit hoặc timeout.`
- Vì vậy, với Overpass, nhóm nên xem đây là pipeline `background/batch` hơn là pipeline cần hoàn tất nhanh trong một lần chạy tươi.

### Geoapify

- Chạy mượt hơn trong thực tế với cùng kiểu batch notebook.
- Không gặp lỗi API trong quá trình test hiện tại.
- Checkpoint tăng đều và file output đồng bộ tốt.
- Trong test hiện tại, notebook đã chạy đủ `100` record và không phát sinh lỗi API.
- Với cùng cách chia batch, cảm nhận thực tế là ổn định hơn rõ rệt so với Overpass.
- Quan sát thực tế hôm nay:
  - notebook đã chạy đủ `100` mẫu
  - theo timestamp của file output/checkpoint, thời gian hoàn tất thực tế cho `100` mẫu là **16 phút 47 giây** (`17:56:30` -> `18:13:17`)
  - tốc độ tăng checkpoint khá đều, không xuất hiện lỗi API trong log
- Cách ghi ngắn gọn trong báo cáo:
  - `Geoapify đã hoàn tất 100 mẫu trong 16 phút 47 giây ở phiên test ngày 2026-07-11.`
- So với Overpass, thời gian hoàn tất của Geoapify ổn định hơn và dễ dự đoán hơn.

## 3. Limit, quota và vận hành

### Overpass

- Dùng `https://overpass-api.de/api/interpreter`
- Public instance có quota động.
- Nên kiểm tra `https://overpass-api.de/api/status` trước khi gọi.
- Có thể bị:
  - `429 Too Many Requests`
  - `504 Gateway Timeout`
- Cần:
  - `batch`
  - `checkpoint`
  - `cache`
  - `retry`
  - `pause` giữa các batch

### Geoapify

- Dùng `https://api.geoapify.com/v2/places`
- Là API thương mại nên hành vi ổn định hơn.
- Free plan hiện tại:
  - `3000 credits/day`
  - `up to 5 requests/second`
- Nếu một request trả `115` places thì tài liệu mô tả chi phí là `6 credits`.
- Cần quản lý API key và kiểm soát số category, bán kính, `limit`.

## 4. Độ đầy dữ liệu

Số lượng giá trị `null` trên các trường khoảng cách ở output hiện tại:

| Field | Overpass null | Geoapify null |
|---|---:|---:|
| `distance_to_nearest_school_m` | 0 | 0 |
| `distance_to_nearest_park_m` | 0 | 0 |
| `distance_to_nearest_hospital_m` | 1 | 27 |
| `distance_to_nearest_supermarket_m` | 1 | 2 |
| `distance_to_nearest_market_m` | 1 | 3 |
| `distance_to_nearest_cafe_m` | 0 | 0 |
| `distance_to_nearest_boulevard_m` | 0 | 0 |

Nhận xét:

- `Overpass` cho độ phủ tốt hơn ở nhóm `hospital`, `supermarket`, `market`.
- `Geoapify` có độ phủ rất tốt ở `school`, `park`, `cafe`, `boulevard`, nhưng thiếu khá nhiều ở `hospital`.
- Với `hospital`, khả năng cao cần tinh chỉnh lại category mapping của Geoapify nếu muốn dùng làm nguồn chính.
- `Overpass` và `Geoapify` đều được tổng hợp trên đủ `100` record, nên bảng so sánh có cùng quy mô dữ liệu.

## 5. Độ ổn định

### Overpass

- Error log hiện tại là `0`, nhưng đây là sau khi đã chỉnh notebook để chịu lỗi tốt hơn.
- Vấn đề chính không nằm ở schema mà ở quota của public instance.
- Phù hợp nếu nhóm muốn dùng nguồn mở, chi phí thấp, chấp nhận thời gian chạy lâu hơn.
- Khi bị rate limit, notebook vẫn có thể resume được nhờ checkpoint, nhưng tổng thời gian hoàn tất sẽ khó dự đoán.

### Geoapify

- Error log hiện tại là `0`.
- Đã chạy đủ `100` record trong notebook test hiện tại.
- Phù hợp nếu nhóm muốn một provider thương mại ổn định hơn để demo hoặc benchmark.
- Tốc độ và tiến độ checkpoint ổn định hơn, phù hợp hơn nếu nhóm muốn rerun nhiều lần.

## 6. Kết luận nhanh

- Nếu ưu tiên `miễn phí / open-data`: dùng `Overpass`, nhưng phải chấp nhận chậm và cần `batch + cache + checkpoint`.
- Nếu ưu tiên `tốc độ chạy và độ ổn định`: `Geoapify` đang tốt hơn trong thực tế test.
- Nếu ưu tiên `độ phủ hospital`: `Overpass` hiện đang nhỉnh hơn `Geoapify` với mapping hiện tại.
- Hướng hợp lý cho nhóm là:
  - dùng `Overpass` như baseline open-data
  - dùng `Geoapify` như provider thương mại để so sánh và demo

## 7. Tài liệu tham chiếu trong repo

- Overpass notebook: [notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb](../notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb)
- Geoapify notebook: [notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb](../notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb)
- Overpass schema: [data/overpass/overpass_enriched_schema_readme.json](../data/overpass/overpass_enriched_schema_readme.json)
- Geoapify schema: [data/geoapify/geoapify_enriched_schema_readme.json](../data/geoapify/geoapify_enriched_schema_readme.json)
- Overpass cURL: [data/overpass/overpass_api_curl_examples.md](../data/overpass/overpass_api_curl_examples.md)
- Geoapify cURL: [data/geoapify/geoapify_api_curl_examples.md](../data/geoapify/geoapify_api_curl_examples.md)
