# Hệ thống tư vấn chọn bất động sản thông minh ở thành phố Hồ Chí Minh

## 1. Mô tả đề tài:

**Thực trạng & Hạn chế**: Việc tìm mua/thuê bất động sản tại TP.HCM rất phức tạp. Các ứng dụng hiện nay chỉ cho phép lọc theo một vài số liệu tường minh như: giá, diện tích, số phòng, khu vực, … chứ không xử lý được **nhu cầu cá nhân** hoặc hiểu được **nhu cầu ẩn** của người dùng (Ví dụ: Công ty ở quận 1 thì muốn tìm các bđs quanh đó, nhu cầu tìm bđs gần công viên để có môi trường thoáng mát cho con nhỏ, có con nhỏ học cấp 2 thì sẽ ưu tiên bđs gần trường học, …).

**Giải pháp của hệ thống**: Xây dựng một Hệ thống hỗ trợ ra quyết định (DSS) thông minh nhằm:
1. Hiểu nhu cầu: Chuyển đổi nhu cầu của người dùng thành các tiêu chí và trọng số để chấm điểm độ tương thích.
2. Khuyến nghị thông minh: Đưa ra Top 5 lựa chọn tối ưu nhất kèm theo lời giải thích bằng ngôn ngữ tự nhiên để người dùng dễ dàng ra quyết định.

## 2. Input và Output của hệ thống
<TBD>

## 3. Nguồn dữ liệu

**2 nguồn dữ liệu** ở đây là:
- Nhu cầu của người dùng (User Input)
- Cơ sở dữ liệu đã được làm giàu của hệ thống (có thêm các thông tin về tiện ích xung quanh) (Enrichment database)

==> Chúng ta sẽ kết hợp 2 nguồn này với nhau để đưa ra gợi ý

## 4. Phân tích dữ liệu

Kế hoạch phân tích dữ liệu. Ví dụ số lượng mẫu, số lượng thuộc tính, kiểu dữ liệu, dữ liệu thiếu, phân bố nhãn, phân bố giá trị quan trọng, các đặc điểm nổi bật của dữ liệu và những khó khăn có thể gặp khi xử lý dữ liệu.

## 5. Solutions

### Baseline cũ Form -> Inference Engine -> LLM explanation (không dùng làm solution chính)
Ý tưởng chính: người dùng nhập nhu cầu qua form cố định, hệ thống chuyển nhu cầu thành tập luật và trọng số, sau đó inference engine lọc và chấm điểm để tạo Top 5, cuối cùng LLM sinh lời giải thích.

Dữ liệu sử dụng: dữ liệu người dùng nhập từ form và cơ sở dữ liệu bất động sản đã được làm giàu với các thuộc tính như giá, số phòng, khoảng cách đến trường học, công viên, trục giao thông.

Cách xử lý: form được chuẩn hóa thành `hard constraints` và `soft preferences`; inference engine thực hiện `rule-based filtering` để loại các phương án không đạt điều kiện bắt buộc, sau đó thực hiện `rule-based scoring` để tính `total_score` cho từng bất động sản; LLM sẽ dùng kết quả Top 5 để sinh ra lời giải thích phù hợp.

Kết quả kỳ vọng: hệ thống tạo ra khuyến nghị minh bạch, dễ kiểm chứng, thời gian xử lý nhanh và phù hợp với các tiêu chí đầu vào tương đối cố định.

pipleline: `Form -> Preference Profile -> Rule-based Filtering -> Rule-based Scoring -> Top 5 Candidates -> LLM Explanation`

Ghi chú cập nhật: hướng này chỉ nên giữ như baseline kỹ thuật hoặc bước tiền xử lý, vì dễ bị đánh giá là bộ lọc/rule-based recommender thông thường và chưa thể hiện rõ bản chất DSS with Data.

### Solution 1 Form + User Query -> Two-LLM Pipeline + Guardrail -> Explanation
Ý tưởng chính: Solution 1 dùng một pipeline tuần tự hai LLM có guardrail. LLM thứ nhất đóng vai trò reasoner: đọc form và nhu cầu tự nhiên, bắt buộc gọi tool lọc dữ liệu, có thể gọi thêm tool enrichment khi người dùng nhắc đến tiện ích chưa có sẵn, sau đó chấm điểm và sinh lý do sơ bộ cho các candidate. LLM thứ hai chỉ sinh giải thích cuối cùng dựa trên Top 5 đã được guardrail kiểm soát.

Dữ liệu sử dụng: cơ sở dữ liệu BĐS đã được làm giàu, form người dùng, nhu cầu free-text và các thuộc tính tiện ích bổ sung được enrich động nếu cần.

Cách xử lý: hệ thống tạo hard constraints từ form, gọi `sql_filter` để lấy candidate set trong database, cho LLM reasoner dùng các trường tiện ích sẵn có hoặc gọi tool enrich thêm tiện ích động, sau đó guardrail bằng code loại property ID không thuộc candidate set, loại trùng, sort theo điểm, đánh lại rank và cắt Top 5. LLM explainer nhận Top 5 đã khóa và viết giải thích trade-off.

Kết quả kỳ vọng: hệ thống linh hoạt hơn baseline rule-based khi xử lý free-text, nhưng vẫn kiểm soát được biên dữ liệu. Top 5 không được bịa ngoài dataset, còn phần explanation phải bám vào thuộc tính thật của bất động sản.

pipeline: `Form + User Query -> Hard Filter -> LLM Reasoner + Tool Use -> Guardrail Grounding -> Top 5 -> LLM Explanation`

### Solution 2 Form + User Query -> Inference Engine + LLM -> LLM explaination
Ý tưởng chính: người dùng vừa nhập form cố định vừa nhập thêm nhu cầu đặc biệt bằng ngôn ngữ tự nhiên; LLM xử lý phần nhu cầu bổ sung, còn inference engine giữ vai trò lọc, chấm điểm và tái xếp hạng.

Dữ liệu sử dụng: dữ liệu từ form, nhu cầu thêm của người dùng, cơ sở dữ liệu bất động sản đã được làm giàu, cùng dữ liệu tiện ích xung quanh lấy thêm từ geocoding và Search Map API.

Cách xử lý: chạy form qua inference engine để lấy Top 10 ban đầu; LLM bóc tách nhu cầu thêm, xử lý cả các nhu cầu bị trùng với form, rồi quy đổi chúng thành `hard constraints`, `soft preferences`; gọi tool để enrichment đồng loạt các nhu cầu thêm (thuộc tính mới) này vào Top 10; sau đó chuẩn hóa điểm, re-ranking và cắt còn Top 5; LLM sinh lời giải thích dựa trên Top 5 này.

Kết quả kỳ vọng: hệ thống giữ được tính minh bạch của rule-based nhưng vẫn xử lý được các nhu cầu mới và mơ hồ hơn; đổi lại chi phí API, độ trễ và độ phức tạp triển khai sẽ cao hơn solution 1.

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

Kế hoạch xây dựng tập validation chi tiết nằm ở `docs/validation_dataset_plan.md`. Tập validation nên gồm 3 phần: validation properties, user scenarios và human relevance labels để so sánh Solution 2 với Solution 1 bằng CSR@5, AvgRel@5, NDCG@5, MAP@5, Pairwise Win Rate, Grounding Pass Rate, tool-call correctness và latency.

## 7. Lưu ý
1. Tiêu chí đánh giá/so sánh (1) và (2) phải dựa trên một cơ sở rõ ràng. Có thể hiểu là phải dựa trên một tập validation nào đó. Tạm thời chấp nhận tập validation là tập do chúng ta tự phân loại/xếp hạng dựa trên sự tổng hợp và suy luận
2. Tên đề tài không cần thay đổi, nhưng có thể giới hạn tập data của hệ thống lại thành 2 hoặc 3 quận, trong mỗi quận này lại chọn 2 hoặc 3 khu vực để xử lí (mục đích là giới hạn lại dữ liệu nhưng vẫn đảm bảo sự đa dạng để chạy demo). Bước 4 sẽ thực hiện việc giới hạn này bằng cách nêu rõ số lượng mẫu và cách xử lí.
