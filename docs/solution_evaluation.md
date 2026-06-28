# Solution Evaluation - Smart Real Estate Advisory System

File này đánh giá 2 solution hiện có trong `source_notes/` và gợi ý cách trình bày với thầy.

## 1. Summary

| Solution | Short name | Core idea | Recommendation |
|---|---|---|---|
| Solution 1 | Rule-based recommender baseline | Form cố định -> luật lọc -> chấm điểm -> Top 5 -> LLM giải thích | Chỉ nên giữ làm baseline kỹ thuật, không nên dùng làm solution chính nếu thầy đánh giá chưa phù hợp DSS |
| Solution 2 | Hybrid LLM + Map enrichment | Form + nhu cầu tự nhiên -> LLM parse -> gọi map/POI API -> re-rank -> LLM giải thích | Nên dùng làm hướng chính/đề xuất nâng cấp |
| Solution 3 | Data-driven MCDA/TOPSIS | User preference + enriched data -> decision matrix -> AHP/Entropy weights -> TOPSIS -> sensitivity analysis | Nên dùng làm solution thay thế Solution 1 vì thể hiện rõ bài toán ra quyết định đa tiêu chí |

## 2. Solution 1 Evaluation

### Pipeline

```text
Form
-> Preference Profile
-> Rule-based Filtering
-> Rule-based Scoring
-> Top 5 Candidates
-> LLM Explanation
```

### Strengths

- Rất hợp với DSS vì có luật, trọng số và điểm số minh bạch.
- Dễ demo với 100-200 listing sạch.
- Không phụ thuộc nhiều vào API bên ngoài nếu database đã có sẵn attributes.
- Dễ giải thích cách hệ thống ra quyết định.
- Dễ đánh giá bằng rule consistency và constraint satisfaction.

### Weaknesses

- Chỉ xử lý tốt các tiêu chí đã có trong form.
- Không linh hoạt với nhu cầu tự nhiên như "gần chợ", "khu yên tĩnh", "nhiều tiện ích cho trẻ em".
- Trọng số dễ bị hỏi: lấy từ đâu, có cơ sở không.
- Nếu attributes nghèo thì recommendation chỉ giống bộ lọc nâng cao.

### What To Improve

Nên làm rõ 3 lớp dữ liệu:

1. `hard_constraints`: ngân sách tối đa, số phòng tối thiểu, quận mong muốn.
2. `soft_preferences`: gần trường, gần công viên, gần bệnh viện, giá/m2 tốt.
3. `weights`: trọng số theo persona hoặc theo form user chọn.

Nên định nghĩa 3-4 persona để test:

| Persona | Priority |
|---|---|
| Family with children | school, park, hospital, bedrooms |
| Young professional | commute, supermarket, center access |
| Investor | price_per_m2, district median, liquidity |
| Elderly buyer | hospital, quiet area, low floor if available |

### Verdict

Solution 1 **chỉ nên giữ làm baseline hoặc bước tiền xử lý**. Nếu thầy đánh giá solution này chưa phù hợp với môn DSS with Data, không nên tiếp tục bảo vệ nó như một hướng chính vì dễ bị xem là bộ lọc nâng cao.

## 3. Solution 2 Evaluation

### Pipeline

```text
Form + Additional User Request
-> LLM Requirement Parsing
-> Deduplication with Form Criteria
-> Amenity Mapping
-> Rule-based Top 10
-> Tool-based Attribute Enrichment
-> Re-scoring / Re-ranking
-> Top 5
-> LLM Explanation
```

### Strengths

- Hợp tinh thần "thông minh" hơn vì hiểu được nhu cầu tự nhiên.
- Tạo khác biệt so với web lọc BĐS bình thường.
- Có thể tận dụng Mapbox/Google/OSM để tạo dynamic attributes.
- Rất phù hợp để show DSS + LLM:
  - DSS engine quyết định bằng điểm số.
  - LLM hiểu nhu cầu và giải thích.
- Có thể xử lý nhu cầu như:
  - "gần trường mẫu giáo"
  - "nhiều quán cafe"
  - "gần chợ"
  - "tránh xa đại lộ"

### Weaknesses

- Phụ thuộc API map/geocoding nếu chưa có lat/lon và POI.
- Dễ tăng độ phức tạp: parse user intent, geocode, search POI, normalize score.
- LLM có rủi ro hallucination nếu không khóa output schema.
- Chi phí và quota API có thể thành rủi ro.
- Nếu chỉ enrich Top 10 sau bước Solution 1, có thể bỏ sót một số listing ngoài Top 10 nhưng rất phù hợp với nhu cầu bổ sung.

### What To Improve

Nên giới hạn scope để khả thi:

```text
Chỉ xử lý 100-200 listing sạch
Chỉ dùng 3-5 loại tiện ích
Chỉ enrich Top 10 hoặc Top 20
Chỉ nhận nhu cầu có thể map sang POI measurable
```

Danh sách amenity nên hỗ trợ ở demo:

| User phrase | Internal amenity | Feature |
|---|---|---|
| gần trường / có con nhỏ | school, kindergarten | nearest_school_m, school_count_1km |
| gần công viên | park | nearest_park_m, park_count_1km |
| gần bệnh viện | hospital, clinic | nearest_hospital_m |
| gần chợ / siêu thị | market, supermarket | market_count_1km |
| tiện đi làm | workplace/district center | commute_distance_m |

LLM output nên bị khóa schema:

```json
{
  "hard_constraints": [],
  "soft_preferences": [
    {
      "user_phrase": "gần trường cho con nhỏ",
      "amenity": "school",
      "metric": "distance_to_nearest_school_m",
      "direction": "lower_better",
      "weight_delta": 0.15,
      "supported": true
    }
  ],
  "unsupported_requirements": []
}
```

### Verdict

Solution 2 **nên là solution chính để trình bày với thầy**, nhưng phải nói rõ đây là bản nâng cấp trên nền Solution 1. Demo có thể làm ở scale nhỏ để kiểm soát API và thời gian.

## 4. Solution 3 Evaluation

### Pipeline

```text
User Preference
-> Hard Constraint Filtering
-> Decision Matrix
-> AHP / Survey-based User Weights
-> Entropy / CRITIC Data Weights
-> Combined Weights
-> TOPSIS Ranking
-> Sensitivity Analysis
-> Top 5
-> LLM Trade-off Explanation
```

### Strengths

- Rất hợp với DSS vì mô hình hóa rõ `alternatives`, `criteria`, `weights`, `decision matrix` và `ranking`.
- Trọng số có cơ sở hơn Solution 1 vì có thể lấy từ AHP/user survey và hiệu chỉnh bằng Entropy/CRITIC từ dữ liệu.
- TOPSIS giải thích được phương án nào gần nghiệm lý tưởng nhất và xa nghiệm xấu nhất.
- Sensitivity analysis giúp trả lời câu hỏi quan trọng của DSS: quyết định có ổn định khi giả định/trọng số thay đổi không?
- Không phụ thuộc mạnh vào LLM hoặc API bên ngoài như Solution 2, nên dễ làm bản demo ổn định.
- Dễ so sánh định lượng với Solution 2 bằng relevance score, NDCG@5, MAP@5 và stability.

### Weaknesses

- Cần giải thích AHP/TOPSIS rõ ràng để người nghe không thấy quá toán.
- Nếu chỉ dùng trọng số tự đặt mà không có survey hoặc pairwise comparison thì sẽ quay lại điểm yếu chủ quan giống Solution 1.
- TOPSIS vẫn phụ thuộc vào chất lượng feature; nếu POI/enrichment sai thì ranking sai theo.
- Cần thêm sensitivity analysis để solution đủ khác biệt và đủ mạnh.

### What To Improve

Nên triển khai Solution 3 với scope vừa phải:

```text
100-300 listings
6-8 criteria
3 persona/user profiles
TOPSIS ranking
10-20% weight perturbation sensitivity analysis
human relevance labels cho 10-20 scenarios nếu kịp
```

Criteria nên dùng:

| Criteria | Direction |
|---|---|
| price_million_vnd | lower better |
| price_per_m2_million | lower better |
| area_m2 | higher better |
| bedrooms | higher better |
| distance_to_nearest_school_m | lower better |
| distance_to_nearest_park_m | lower better |
| distance_to_nearest_hospital_m | lower better |
| distance_to_nearest_supermarket_m | lower better |

### Verdict

Solution 3 **nên dùng làm solution thay thế Solution 1**. Đây là hướng hợp môn DSS hơn vì trọng tâm không phải "lọc rồi cộng điểm", mà là ra quyết định đa tiêu chí có trọng số, nghiệm lý tưởng, phân tích nhạy cảm và kiểm chứng bằng dữ liệu.

## 5. Recommended Architecture

Không nên để LLM tự quyết định ranking. Kiến trúc nên là:

```text
LLM = preference parser + explanation generator
Inference engine = filtering + scoring + ranking
Map/POI tool = evidence/data provider
```

Lý do:

- Tránh LLM bịa ranking.
- Giữ được tính giải thích và kiểm chứng.
- Dễ bảo vệ trước thầy vì DSS có luật và score rõ ràng.

## 6. Data Requirements By Solution

| Requirement | Solution 1 | Solution 2 |
|---|---|---|
| Clean real estate listing | Required | Required |
| Price/area/bedrooms/location | Required | Required |
| Precomputed amenities | Recommended | Optional |
| Lat/lon | Recommended | Required if using map API |
| Mapbox/Google/OSM | Optional | Required for dynamic enrichment |
| LLM | Explanation only | Parsing + explanation |
| API key | Not required if attributes exist | Required for Mapbox/Google |

| Requirement | Solution 3 |
|---|---|
| Clean real estate listing | Required |
| Enriched criteria/features | Required |
| User preference / persona weights | Required |
| AHP pairwise comparison or survey | Recommended |
| Entropy/CRITIC data weighting | Recommended |
| Human relevance validation | Recommended |
| LLM | Explanation only |
| API key | Not required if features are precomputed |

## 7. Evaluation Plan

Protocol chi tiết cho validation dataset nằm ở:

```text
docs/validation_dataset_plan.md
```

File này nên được dùng làm cơ sở cho final report vì nó tách rõ technical validation, property holdout validation và human-labeled decision-quality validation.

### For Solution 1

| Metric | Meaning |
|---|---|
| Constraint satisfaction | Top 5 có vi phạm ngân sách/số phòng/quận không |
| Score transparency | Mỗi recommendation có breakdown điểm không |
| Ranking stability | Cùng input có ra cùng kết quả không |
| Persona relevance | Top 5 có hợp persona không |

### For Solution 2

| Metric | Meaning |
|---|---|
| Intent parsing accuracy | LLM parse nhu cầu đúng không |
| Amenity mapping accuracy | Nhu cầu có map đúng sang POI không |
| Re-ranking usefulness | Ranking sau enrichment có hợp lý hơn không |
| Explanation faithfulness | LLM giải thích có dựa đúng score/attribute không |
| Latency/cost | Có chạy được trong demo không |

### For Solution 3

| Metric | Meaning |
|---|---|
| Constraint satisfaction | Top 5 có vi phạm hard constraints không |
| AHP consistency ratio | Preference người dùng có nhất quán không |
| Average Top-5 TOPSIS score | Chất lượng tổng thể của Top 5 theo MCDA |
| Top-5 stability | Ranking có ổn định khi trọng số thay đổi không |
| Critical criteria | Tiêu chí nào làm ranking nhạy nhất |
| Human relevance / NDCG@5 | Top 5 có khớp nhãn người đánh giá không |

## 8. Risks And Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Kaggle dataset thiếu lat/lon | Không tính được khoảng cách | Geocode 100-200 mẫu bằng Mapbox/Google |
| API quota/cost | Demo fail hoặc tốn phí | Dùng OSM offline hoặc cache kết quả API |
| LLM parse sai nhu cầu | Ranking lệch | Dùng JSON schema + whitelist amenity |
| Trọng số chủ quan | Bị hỏi cơ sở | Dùng persona-based weights và ghi rõ là baseline rule |
| Search API trả kết quả không ổn định | Reproducibility thấp | Cache POI result thành dataset trung gian |
| Solution 3 bị giống weighted scoring | Thầy có thể xem là biến thể Solution 1 | Nhấn mạnh AHP/Entropy, TOPSIS ideal solution và sensitivity analysis |
| Trọng số AHP chủ quan | Ranking phụ thuộc người dùng | Thu thập survey/pairwise comparison và báo cáo Consistency Ratio |

## 9. Presentation Recommendation

Khi trình bày với thầy, nên nói:

1. Nhóm không dùng Solution 1 làm solution chính nữa:
   - Solution 1 chỉ là baseline rule-based ban đầu
   - hạn chế là trọng số và luật còn thủ công
   - chưa đủ mạnh để đại diện cho DSS with Data

2. Nhóm ưu tiên **phương án 2** vì xử lý nhu cầu linh hoạt:
   - listing BĐS là dữ liệu sản phẩm
   - POI/amenity là dữ liệu ngữ cảnh
   - hệ thống tạo attribute quyết định và recommend Top 5

3. Nhóm bổ sung **phương án 3** làm hướng DSS/MCDA:
   - mô hình hóa alternatives, criteria, weights và decision matrix
   - dùng TOPSIS để tìm phương án gần nghiệm lý tưởng nhất
   - dùng sensitivity analysis để kiểm tra độ ổn định của quyết định

4. Hai solution chính không loại trừ nhau:
   - Solution 2 mạnh về hiểu nhu cầu tự nhiên và enrich dữ liệu động
   - Solution 3 mạnh về phương pháp ra quyết định đa tiêu chí và kiểm chứng trade-off

## 10. Suggested Final Scope For Midterm

Scope nên chốt:

```text
100-200 listings in Ho Chi Minh City
3-5 amenity types
3 persona test cases
Top 5 recommendation
LLM explanation based only on scoring evidence
```

Đây là scope vừa đủ để demo, không bị sa vào làm full app BĐS.
