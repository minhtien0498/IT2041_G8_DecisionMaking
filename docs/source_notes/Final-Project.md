# Hệ thống tư vấn chọn bất động sản thông minh ở thành phố Hồ Chí Minh

## 1. Mô tả đề tài:

**Thực trạng & Hạn chế**: Việc tìm mua/thuê bất động sản tại TP.HCM rất phức tạp. Các ứng dụng hiện nay chỉ cho phép lọc theo một vài số liệu tường minh như: giá, diện tích, số phòng, khu vực, … chứ không xử lý được **nhu cầu cá nhân** hoặc hiểu được **nhu cầu ẩn** của người dùng (Ví dụ: Công ty ở quận 1 thì muốn tìm các bđs quanh đó, nhu cầu tìm bđs gần công viên để có môi trường thoáng mát cho con nhỏ, có con nhỏ học cấp 2 thì sẽ ưu tiên bđs gần trường học, …).

**Giải pháp của hệ thống**: Xây dựng một Hệ thống hỗ trợ ra quyết định (DSS) thông minh nhằm:
1. Hiểu nhu cầu: Chuyển đổi nhu cầu của người dùng thành các tiêu chí và trọng số để chấm điểm độ tương thích.
2. Khuyến nghị thông minh: Đưa ra Top 5 lựa chọn tối ưu nhất kèm theo lời giải thích bằng ngôn ngữ tự nhiên để người dùng dễ dàng ra quyết định.

## 2. Input và Output của hệ thống

**Input chung cho cả hai solution:**
Cả Solution 5.1 và Solution 5.2 đều nhận cùng một dạng input để đảm bảo so sánh công bằng.
- **Form cố định**: các tiêu chí cơ bản có thể định lượng được (ngân sách, số phòng ngủ, khoảng cách tối đa đến trường học / công viên / trục giao thông).
- **Nhu cầu thêm** *(tùy chọn)*: mô tả tự do bằng ngôn ngữ tự nhiên cho các mong muốn bổ sung mà form chưa bao phủ.

Hai solution xử lý cùng input này theo cách khác nhau, đó là điểm khác biệt cốt lõi được đem ra so sánh.

**Output chung:**
- Top 5 bất động sản được khuyến nghị.
- Lời giải thích bằng ngôn ngữ tự nhiên cho từng lựa chọn.

## 3. Nguồn dữ liệu

**2 nguồn dữ liệu** ở đây là:

**Nguồn 1 — Dữ liệu BĐS gốc:**
- Dataset: *Ho Chi Minh City Real Estate Data 2025* (Kaggle)
- Quy mô gốc: 51,000+ listings toàn TP.HCM
- Phạm vi demo: lọc xuống còn **37 BĐS nhà riêng tại Quận Gò Vấp** (file `go_vap_30.json`)
- Gồm: giá, diện tích, số phòng ngủ/phòng tắm, số tầng, vị trí, tọa độ GPS, mô tả

**Nguồn 2 — Dữ liệu tiện ích xung quanh (POI Enrichment):**
- Tọa độ các tiện ích (trường học, bệnh viện, công viên, siêu thị, trục đại lộ) thu thập từ Google Maps / OpenStreetMap
- Khoảng cách tính bằng công thức **Haversine** (đường chim bay)
- Kết quả lưu trong file `go_vap_enriched.json` (thêm 10 thuộc tính mới cho mỗi BĐS)

==> Kết hợp 2 nguồn này để đưa ra gợi ý cá nhân hóa

## 4. Phân tích dữ liệu

**Phạm vi dữ liệu demo:** 1 quận (Gò Vấp), 6 phường (Thông Tây Hội, An Hội Tây, An Hội Đông, Hạnh Thông, An Nhơn, An Phú Đông).

### 4.1 Dữ liệu BĐS gốc (`go_vap_30.json`)

| Chỉ số | Giá trị |
|---|---|
| Số mẫu | 37 BĐS (loại: Nhà riêng) |
| Số thuộc tính | 22 |
| Giá | 2.85 – 27.0 tỷ VND, trung bình **9.34 tỷ** |
| Diện tích | 26 – 258.4 m², trung bình **79.0 m²** |
| Số phòng ngủ | 1 – 7 phòng |
| Vị trí | Đường chính / Trong hẻm |

**Phân bố theo phường:**

| Phường | Số BĐS |
|---|---|
| Thông Tây Hội | 13 |
| An Hội Tây | 10 |
| An Hội Đông | 8 |
| Hạnh Thông | 4 |
| An Nhơn | 1 |
| An Phú Đông | 1 |

**Dữ liệu thiếu:** Cột `direction` (hướng nhà) có nhiều null; các cột khoảng cách tiện ích đều null — cần bước enrichment.

### 4.2 Dữ liệu sau làm giàu (`go_vap_enriched.json`)

| Chỉ số | Giá trị |
|---|---|
| Số mẫu | 37 BĐS (giữ nguyên) |
| Số thuộc tính | 32 (thêm 10 thuộc tính POI) |

**Khoảng cách đến tiện ích gần nhất (sau enrichment):**

| Tiện ích | Min | Max | Trung bình | Null |
|---|---|---|---|---|
| Trường học | 110 m | 3,628 m | 892 m | 0/37 |
| Công viên | 121 m | 2,644 m | 939 m | 0/37 |
| Bệnh viện | 136 m | 4,351 m | 1,220 m | 0/37 |
| Siêu thị | 83 m | 3,965 m | 1,050 m | 0/37 |
| Đại lộ chính | 191 m | 1,866 m | 839 m | 0/37 |

**10 thuộc tính mới thêm vào mỗi BĐS:** `nearest_*_name`, `near_*_count_1km` cho 5 loại tiện ích.

### 4.3 Khó khăn khi xử lý dữ liệu
- Dataset nhỏ (37 mẫu) — phù hợp để demo nhưng cần mở rộng nếu scale production
- Cột `direction` thiếu nhiều — không đưa vào scoring
- Khoảng cách POI trong dữ liệu gốc đều null, bắt buộc phải qua bước enrichment trước khi chạy pipeline
- Số lượng POI tham chiếu còn hạn chế (tọa độ thu thập thủ công), có thể không phản ánh đầy đủ thực tế địa bàn

## 5. Solutions

### 5.1 Form + Free-Text -> Fuzzy LLM Reasoning -> Iterative Search -> Top 5 + Tradeoff Explanation
Ý tưởng chính: nhận cùng input (form + nhu cầu thêm) như solution 5.2, nhưng LLM gộp toàn bộ thành một mô tả ngữ nghĩa thống nhất rồi dùng fuzzy reasoning để xác định các chiều mơ hồ, thực hiện tìm kiếm lặp từ nhiều góc độ, phân nhóm kết quả thành các cluster và giải thích tradeoff rõ ràng.

Dữ liệu sử dụng: form + nhu cầu thêm (được LLM chuyển thành câu mô tả tổng hợp), cơ sở dữ liệu bất động sản với vector embedding (mô tả, tiện ích, khu vực) và metadata dạng SQL (giá, số phòng, diện tích).

Cách xử lý: LLM gộp form và nhu cầu thêm thành một biểu diễn ngữ nghĩa thống nhất; xác định các chiều mơ hồ (chất lượng, giá, vị trí, tiện ích); sinh ra nhiều câu truy vấn ngữ nghĩa khác nhau cho từng diễn giải; thực hiện multi-round vector search; phân nhóm kết quả thành các cluster đặc trưng (ví dụ: sống động, yên tĩnh, cân bằng); tính fuzzy satisfaction score [0, 1] cho từng chiều; áp SQL filter nếu có hard constraint tường minh; chọn Top 5 đa dạng từ nhiều cluster; LLM sinh lời giải thích tradeoff đầy đủ theo từng nhóm.

Kết quả kỳ vọng: hệ thống hiểu được nhu cầu mơ hồ, đưa ra Top 5 đa dạng từ nhiều hướng, kèm lời giải thích tradeoff minh bạch giúp người dùng nhìn thấy các lựa chọn khác nhau và ra quyết định phù hợp với ưu tiên thực sự của họ.

Pipeline: `Form + Free-Text → LLM Semantic Fusion → Fuzzy Analysis → Multi-Round Vector Search → Result Clustering → Tradeoff Analysis → SQL Filtering (nếu có) → Top 5 Selection → LLM Explanation with Tradeoff`

### 5.2 Form + User Query -> Inference Engine + LLM -> LLM explaination
Ý tưởng chính: người dùng vừa nhập form cố định vừa nhập thêm nhu cầu đặc biệt bằng ngôn ngữ tự nhiên; LLM xử lý phần nhu cầu bổ sung, còn inference engine giữ vai trò lọc, chấm điểm và tái xếp hạng.

Dữ liệu sử dụng: dữ liệu từ form, nhu cầu thêm của người dùng, cơ sở dữ liệu bất động sản đã được làm giàu, cùng dữ liệu tiện ích xung quanh lấy thêm từ geocoding và Search Map API.

Cách xử lý: chạy form qua inference engine để lấy Top 10 ban đầu; LLM bóc tách nhu cầu thêm, xử lý cả các nhu cầu bị trùng với form, rồi quy đổi chúng thành `hard constraints`, `soft preferences`; gọi tool để enrichment đồng loạt các nhu cầu thêm (thuộc tính mới) này vào Top 10; sau đó chuẩn hóa điểm, re-ranking và cắt còn Top 5; LLM sinh lời giải thích dựa trên Top 5 này.

Kết quả kỳ vọng: hệ thống giữ được tính minh bạch của rule-based nhưng vẫn xử lý được các nhu cầu mới và mơ hồ hơn; đổi lại chi phí API, độ trễ và độ phức tạp triển khai sẽ cao hơn solution 5.1.

pipeline: `Form + Additional User Request -> LLM Requirement Parsing and Deduplication -> Amenity Mapping -> Rule-based Top 10 -> Tool-based Attribute Enrichment -> Re-scoring/Re-ranking -> Top 5 -> LLM Explanation`

## 6. Tiêu chí đánh giá/so sánh

Các tiêu chí đánh giá:
1. Độ phù hợp khuyến nghị
2. Chất lượng lời giải thích
3. Thời gian xử lí
4. Khả năng triển khai (mức độ)
5. Chi Phí tính toán
6. Khả năng mở rộng
7. Mức độ hữu ích
8. TBD

## 7. Lưu ý
1. Tiêu chí đánh giá/so sánh (1) và (2) phải dựa trên một cơ sở rõ ràng. Có thể hiểu là phải dựa trên một tập validation nào đó. Tạm thời chấp nhận tập validation là tập do chúng ta tự phân loại/xếp hạng dựa trên sự tổng hợp và suy luận
2. Tên đề tài không cần thay đổi, nhưng có thể giới hạn tập data của hệ thống lại thành 2 hoặc 3 quận, trong mỗi quận này lại chọn 2 hoặc 3 khu vực để xử lí (mục đích là giới hạn lại dữ liệu nhưng vẫn đảm bảo sự đa dạng để chạy demo). Bước 4 sẽ thực hiện việc giới hạn này bằng cách nêu rõ số lượng mẫu và cách xử lí.

## 8. Kế hoạch triển khai và quản lí tiến độ
- Xem kế hoạch triển khai theo tuần và bảng quản lí tiến độ tại file `Implementation-Plan.md`.
- Mẫu tạo validation set tại file `Validation-Set-Template.md`.
