# Solution Evaluation - Smart Real Estate Advisory System

File này đánh giá 2 solution final hiện tại và gợi ý cách trình bày với thầy.

Ghi chú:
- `Solution 1` hiện tại là hướng `MCDA/TOPSIS` của `Phú`, được đổi tên từ `Solution 3` cũ.
- Hướng rule-based `Solution 1` cũ đã bị loại khỏi scope final vì quá đơn giản so với yêu cầu môn.

## 1. Summary

| Solution | Short name | Core idea | Recommendation |
|---|---|---|---|
| Solution 1 | Data-driven MCDA/TOPSIS | User preference + enriched data -> decision matrix -> AHP/Entropy weights -> TOPSIS -> sensitivity analysis | Là một trong hai hướng final chính, hợp DSS hơn |
| Solution 2 | Hybrid LLM + Map enrichment | Form + nhu cầu tự nhiên -> LLM parse -> gọi map/POI API -> re-rank -> LLM giải thích | Là một trong hai hướng final chính, mạnh về cá nhân hóa |

## 2. Ghi chú về hướng cũ đã bị loại

Hướng `Solution 1` cũ từng có pipeline:

```text
Form
-> Preference Profile
-> Rule-based Filtering
-> Rule-based Scoring
-> Top 5 Candidates
-> LLM Explanation
```

Nhóm không còn dùng hướng này làm solution final vì:
- quá gần với bộ lọc/rule-based recommender thông thường
- chưa thể hiện đủ rõ mô hình ra quyết định của DSS
- theo góp ý của thầy, cần đổi sang hướng mạnh hơn về DSS with Data

Phần này chỉ nên nhắc ngắn như một baseline/historical reference nếu cần.

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

## 4. Solution 1 Evaluation

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

Nên triển khai Solution 1 với scope vừa phải:

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

Solution 1 **nên được dùng như một trong hai hướng final chính**. Đây là hướng hợp môn DSS hơn vì trọng tâm không phải "lọc rồi cộng điểm", mà là ra quyết định đa tiêu chí có trọng số, nghiệm lý tưởng, phân tích nhạy cảm và kiểm chứng bằng dữ liệu.

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
| Enriched criteria/features | Required | Optional nhưng rất hữu ích |
| User preference / persona weights | Required | Required |
| AHP pairwise comparison or survey | Recommended | Optional |
| Entropy/CRITIC data weighting | Recommended | Không bắt buộc |
| Mapbox/Google/OSM | Không bắt buộc nếu features đã precompute | Required nếu enrich động |
| LLM | Explanation only | Parsing + explanation |
| API key | Không bắt buộc nếu features đã precompute | Required nếu dùng provider ngoài |

## 7. Evaluation Plan

Protocol chi tiết cho validation dataset nằm ở:

```text
docs/validation_dataset_plan.md
```

File này nên được dùng làm cơ sở cho final report vì nó tách rõ technical validation, property holdout validation và human-labeled decision-quality validation.

### For Solution 2

| Metric | Meaning |
|---|---|
| Intent parsing accuracy | LLM parse nhu cầu đúng không |
| Amenity mapping accuracy | Nhu cầu có map đúng sang POI không |
| Re-ranking usefulness | Ranking sau enrichment có hợp lý hơn không |
| Explanation faithfulness | LLM giải thích có dựa đúng score/attribute không |
| Latency/cost | Có chạy được trong demo không |

### For Solution 1

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
| Solution 1 bị giống weighted scoring | Thầy có thể xem là biến thể scoring thông thường | Nhấn mạnh AHP/Entropy, TOPSIS ideal solution và sensitivity analysis |
| Trọng số AHP chủ quan | Ranking phụ thuộc người dùng | Thu thập survey/pairwise comparison và báo cáo Consistency Ratio |

## 9. Presentation Recommendation

Khi trình bày với thầy, nên nói:

1. Hướng rule-based cũ đã bị loại:
   - quá đơn giản
   - dễ bị xem là bộ lọc nâng cao
   - không còn là solution active nữa

2. Nhóm ưu tiên giữ **2 hướng final**:
   - `Solution 2` mạnh về xử lý nhu cầu linh hoạt
   - `Solution 1` mạnh về mô hình ra quyết định đa tiêu chí

3. Với **phương án 2**:
   - listing BĐS là dữ liệu sản phẩm
   - POI/amenity là dữ liệu ngữ cảnh
   - hệ thống tạo attribute quyết định và recommend Top 5

4. Với **phương án 1**:
   - mô hình hóa alternatives, criteria, weights và decision matrix
   - dùng TOPSIS để tìm phương án gần nghiệm lý tưởng nhất
   - dùng sensitivity analysis để kiểm tra độ ổn định của quyết định

5. Hai solution chính không loại trừ nhau:
   - Solution 2 mạnh về hiểu nhu cầu tự nhiên và enrich dữ liệu động
   - Solution 1 mạnh về phương pháp ra quyết định đa tiêu chí và kiểm chứng trade-off

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
