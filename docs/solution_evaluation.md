# Solution Evaluation - Smart Real Estate Advisory System

File này đánh giá 2 solution hiện có trong `source_notes/` và gợi ý cách trình bày với thầy.

## 1. Summary

| Solution | Short name | Core idea | Recommendation |
|---|---|---|---|
| 5.1 | Rule-based DSS baseline | Form cố định -> luật lọc -> chấm điểm -> Top 5 -> LLM giải thích | Nên dùng làm baseline chắc chắn cho midterm |
| 5.2 | Hybrid LLM + Map enrichment | Form + nhu cầu tự nhiên -> LLM parse -> gọi map/POI API -> re-rank -> LLM giải thích | Nên dùng làm hướng chính/đề xuất nâng cấp |

## 2. Solution 5.1 Evaluation

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

Solution 5.1 **nên giữ**. Đây là baseline an toàn nhất để nhóm không bị vỡ deadline.

## 3. Solution 5.2 Evaluation

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
- Nếu chỉ enrich Top 10 sau bước 5.1, có thể bỏ sót một số listing ngoài Top 10 nhưng rất phù hợp với nhu cầu bổ sung.

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

Solution 5.2 **nên là solution chính để trình bày với thầy**, nhưng phải nói rõ đây là bản nâng cấp trên nền 5.1. Demo có thể làm ở scale nhỏ để kiểm soát API và thời gian.

## 4. Recommended Architecture

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

## 5. Data Requirements By Solution

| Requirement | Solution 5.1 | Solution 5.2 |
|---|---|---|
| Clean real estate listing | Required | Required |
| Price/area/bedrooms/location | Required | Required |
| Precomputed amenities | Recommended | Optional |
| Lat/lon | Recommended | Required if using map API |
| Mapbox/Google/OSM | Optional | Required for dynamic enrichment |
| LLM | Explanation only | Parsing + explanation |
| API key | Not required if attributes exist | Required for Mapbox/Google |

## 6. Evaluation Plan

### For Solution 5.1

| Metric | Meaning |
|---|---|
| Constraint satisfaction | Top 5 có vi phạm ngân sách/số phòng/quận không |
| Score transparency | Mỗi recommendation có breakdown điểm không |
| Ranking stability | Cùng input có ra cùng kết quả không |
| Persona relevance | Top 5 có hợp persona không |

### For Solution 5.2

| Metric | Meaning |
|---|---|
| Intent parsing accuracy | LLM parse nhu cầu đúng không |
| Amenity mapping accuracy | Nhu cầu có map đúng sang POI không |
| Re-ranking usefulness | Ranking sau enrichment có hợp lý hơn không |
| Explanation faithfulness | LLM giải thích có dựa đúng score/attribute không |
| Latency/cost | Có chạy được trong demo không |

## 7. Risks And Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Kaggle dataset thiếu lat/lon | Không tính được khoảng cách | Geocode 100-200 mẫu bằng Mapbox/Google |
| API quota/cost | Demo fail hoặc tốn phí | Dùng OSM offline hoặc cache kết quả API |
| LLM parse sai nhu cầu | Ranking lệch | Dùng JSON schema + whitelist amenity |
| Trọng số chủ quan | Bị hỏi cơ sở | Dùng persona-based weights và ghi rõ là baseline rule |
| Search API trả kết quả không ổn định | Reproducibility thấp | Cache POI result thành dataset trung gian |

## 8. Presentation Recommendation

Khi trình bày với thầy, nên nói:

1. Nhóm ưu tiên **phương án 2** vì đúng DSS hơn:
   - listing BĐS là dữ liệu sản phẩm
   - POI/amenity là dữ liệu ngữ cảnh
   - hệ thống tạo attribute quyết định và recommend Top 5

2. Nhóm giữ **phương án 1** làm fallback:
   - nếu API/geocoding không kịp
   - vẫn có thể demo rule-based recommender từ 2 dataset Kaggle

3. Hai solution không loại trừ nhau:
   - 5.1 là baseline bắt buộc
   - 5.2 là nâng cấp thông minh

## 9. Suggested Final Scope For Midterm

Scope nên chốt:

```text
100-200 listings in Ho Chi Minh City
3-5 amenity types
3 persona test cases
Top 5 recommendation
LLM explanation based only on scoring evidence
```

Đây là scope vừa đủ để demo, không bị sa vào làm full app BĐS.

