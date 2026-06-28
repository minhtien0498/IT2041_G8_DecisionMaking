# Validation Dataset Plan - DSS with Data Real Estate Advisory

Tài liệu này mô tả chi tiết cách xây dựng **tập data validation** cho đề tài Hệ thống tư vấn chọn bất động sản thông minh. Mục tiêu là giúp nhóm trả lời được câu hỏi:

```text
Làm sao biết Top 5 bất động sản mà hệ thống đề xuất là phù hợp, đúng hơn, hoặc tốt hơn giữa các solution?
```

Vì bài toán tư vấn BĐS không có nhãn đúng/sai tự nhiên như classification, validation dataset cần được tạo theo hướng:

```text
User scenario
+ Candidate property set
+ Human/manual relevance labels
+ Evaluation metrics
```

Kế hoạch khảo sát chi tiết nằm ở:

```text
docs/survey_validation_plan.md
```

File đó mô tả cách thiết kế preference survey, labeling survey, quy mô mẫu, rubric chấm nhãn và cách chuyển survey response thành validation scenario.

## 1. Phân biệt các loại validation trong project

Project nên tách rõ 3 lớp validation:

| Loại validation | File/dữ liệu | Mục tiêu | Có dùng làm bằng chứng recommendation đúng với người thật không? |
|---|---|---|---|
| Technical validation | `data/validation_50_scenarios.json` | Test thuật toán ổn định, không crash, không vi phạm hard constraints | Không |
| Property holdout validation | Một subset từ `docs/data_public.csv` | Test pipeline chạy được trên listing mới, dữ liệu mới, quận mới | Không trực tiếp |
| Human-labeled validation | `data/user_preference_validation.json` | Đánh giá Top 5 có phù hợp với nhu cầu người dùng không | Có |

Phần quan trọng nhất cho final là **human-labeled validation**, vì đây là phần biến DSS từ "có chạy được" thành "ra quyết định có chất lượng".

## 2. Dataset cần có những bảng nào

Nên tách validation dataset thành 3 file để dễ quản lý:

```text
data/validation_properties.json
data/validation_user_scenarios.json
data/user_preference_validation.json
```

### 2.1. `validation_properties.json`

Đây là tập BĐS dùng riêng cho validation. Có thể lấy từ `docs/data_public.csv`, sau đó clean và enrich POI.

Mục tiêu:

- Không dùng đúng 37 BĐS Gò Vấp hiện tại nếu muốn final mạnh hơn.
- Nên có 100-300 listing sạch.
- Nên phủ 2-4 khu vực để recommendation không bị quá hẹp.

Schema đề xuất:

```json
{
  "property_id": "VAL_PROP_001",
  "title": "Nhà riêng 3 tầng gần Phan Văn Trị",
  "district": "Gò Vấp",
  "ward": "Phường 7",
  "location_raw": "Đường Phan Văn Trị, Phường 7, Gò Vấp, TP.HCM",
  "price_million_vnd": 6200,
  "area_m2": 58,
  "price_per_m2_million": 106.9,
  "bedrooms": 3,
  "bathrooms": 3,
  "floors": 3,
  "position": "Trong hẻm",
  "latitude": 10.8342,
  "longitude": 106.6731,
  "description_snippet": "Gần trường, siêu thị, khu dân cư an ninh...",
  "distance_to_nearest_school_m": 420,
  "distance_to_nearest_park_m": 900,
  "distance_to_nearest_hospital_m": 1600,
  "distance_to_nearest_supermarket_m": 350,
  "distance_to_nearest_boulevard_m": 300,
  "near_school_count_1km": 4,
  "near_park_count_1km": 1,
  "near_hospital_count_1km": 0,
  "near_supermarket_count_1km": 3,
  "data_split": "validation"
}
```

Tiêu chí chọn listing:

| Điều kiện | Lý do |
|---|---|
| Có giá, diện tích, số phòng ngủ | Đây là hard constraints cơ bản |
| Có lat/lon hoặc geocode được | Cần tính POI/distance |
| Giá trong khoảng hợp lý | Tránh outlier làm méo ranking |
| Diện tích trong khoảng hợp lý | Tránh data lỗi |
| Không trùng listing | Tránh Top 5 gồm các bản ghi lặp |
| Mô tả không quá rỗng | Cần cho Solution 2/LLM explanation |

Quy mô khuyến nghị:

| Mức | Số listing | Khi nào dùng |
|---|---:|---|
| Tối thiểu | 50-100 | Nếu deadline gấp |
| Khá ổn | 100-300 | Phù hợp final project |
| Mạnh | 500-1000 | Nếu có thời gian clean/enrich |

### 2.2. `validation_user_scenarios.json`

Đây là tập nhu cầu người dùng dùng để chạy các solution. Scenario có thể đến từ khảo sát thật, nhóm tự tạo theo persona, hoặc kết hợp cả hai.

Schema đề xuất:

```json
{
  "scenario_id": "REAL_001",
  "source": "survey",
  "persona": "family_with_children",
  "user_need_text": "Gia đình 4 người, có 2 con nhỏ, ngân sách dưới 6 tỷ, cần ít nhất 3 phòng ngủ, ưu tiên gần trường và công viên.",
  "hard_constraints": {
    "budget_max_million": 6000,
    "min_bedrooms": 3,
    "preferred_districts": ["Gò Vấp", "Tân Bình"]
  },
  "importance_1_to_5": {
    "price": 5,
    "area": 3,
    "school": 5,
    "park": 4,
    "hospital": 3,
    "supermarket": 4,
    "transport": 2,
    "quiet_area": 3
  },
  "ahp_pairwise_available": false,
  "created_at": "2026-06-14"
}
```

Persona nên có:

| Persona | Nhu cầu chính | Tiêu chí thường quan trọng |
|---|---|---|
| Family with children | Gia đình có con nhỏ | trường học, công viên, bệnh viện, số phòng ngủ |
| Young professional | Người trẻ đi làm | giá, giao thông, siêu thị, tiện ích |
| Investor | Nhà đầu tư | giá/m2, vị trí, đường lớn, khả năng cho thuê |
| Elderly | Người cao tuổi | bệnh viện, công viên, yên tĩnh, ít di chuyển |
| Couple | Cặp đôi trẻ | ngân sách, tiện ích, diện tích vừa đủ, trường học nếu sắp có con |

Quy mô scenario:

| Mức | Số scenario | Ghi chú |
|---|---:|---|
| Tối thiểu | 10 | Đủ demo metric cơ bản |
| Khuyến nghị | 20-30 | Đủ chia theo persona |
| Tốt | 50 | Có thể báo cáo theo từng persona |

Phân bổ khuyến nghị cho 30 scenario:

| Persona | Số scenario |
|---|---:|
| Family with children | 8 |
| Young professional | 6 |
| Investor | 6 |
| Elderly | 5 |
| Couple | 5 |

## 3. Human-labeled validation là gì

File quan trọng nhất nên là:

```text
data/user_preference_validation.json
```

Mỗi record đại diện cho một scenario đã được chạy qua các solution, sau đó có người chấm mức độ phù hợp của từng BĐS ứng viên.

Schema đầy đủ:

```json
{
  "scenario_id": "REAL_001",
  "persona": "family_with_children",
  "user_need_text": "Gia đình 4 người, có 2 con nhỏ, ngân sách dưới 6 tỷ, cần ít nhất 3 phòng ngủ, ưu tiên gần trường và công viên.",
  "candidate_generation": {
    "method": "union_top10_from_solutions",
    "solution_ids": ["Solution 2", "Solution 3"],
    "candidate_count": 12
  },
  "candidates": [
    {
      "property_id": "VAL_PROP_001",
      "solution_2_rank": 1,
      "solution_3_rank": 3,
      "shown_to_labeler": true
    }
  ],
  "labels": [
    {
      "labeler_id": "L01",
      "property_id": "VAL_PROP_001",
      "relevance_1_to_5": 5,
      "hard_constraint_ok": true,
      "reason": "Đúng ngân sách, đủ 3 phòng ngủ, gần trường và siêu thị."
    },
    {
      "labeler_id": "L02",
      "property_id": "VAL_PROP_001",
      "relevance_1_to_5": 4,
      "hard_constraint_ok": true,
      "reason": "Phù hợp nhưng công viên hơi xa."
    }
  ],
  "aggregated_labels": {
    "VAL_PROP_001": {
      "mean_relevance": 4.5,
      "median_relevance": 4.5,
      "is_relevant_threshold_4": true
    }
  }
}
```

## 4. Cách tạo candidate set để chấm nhãn

Không nên chỉ chấm Top 5 của một solution, vì như vậy validation sẽ thiên vị solution đó. Nên tạo candidate set bằng cách lấy hợp của nhiều nguồn.

Với mỗi scenario:

```text
candidate_set =
  Top 10 từ solution 2
  union Top 10 từ solution 3
  union 5 random valid candidates sau hard filtering
```

Sau đó bỏ trùng, thường còn khoảng 10-20 BĐS/scenario.

Lý do thêm random valid candidates:

- Có negative/neutral examples để metric meaningful hơn.
- Tránh tình trạng tất cả candidate đều quá tốt nên khó phân biệt.
- Giúp kiểm tra solution có thật sự xếp item tốt lên cao hơn item trung bình không.

Nếu thiếu thời gian, dùng bản tối thiểu:

```text
candidate_set = union(Top 10 solution 2, Top 10 solution 3)
```

## 5. Rubric chấm relevance

Nên dùng thang 1-5 vì dễ cho người chấm, đồng thời dùng được cho NDCG.

| Điểm | Ý nghĩa | Mô tả |
|---:|---|---|
| 5 | Rất phù hợp | Thỏa hard constraints, khớp hầu hết tiêu chí quan trọng, ít trade-off |
| 4 | Phù hợp | Thỏa hard constraints, khớp nhiều tiêu chí chính, có một vài điểm trừ |
| 3 | Tạm chấp nhận | Không sai nghiêm trọng, nhưng chỉ khớp một phần nhu cầu |
| 2 | Ít phù hợp | Có nhiều điểm lệch nhu cầu, chỉ nên xem như phương án dự phòng |
| 1 | Không phù hợp | Vi phạm hard constraints hoặc lệch rõ so với nhu cầu |

Quy tắc bắt buộc:

- Nếu vượt ngân sách cứng nhiều hoặc thiếu phòng ngủ tối thiểu, điểm tối đa là 2.
- Nếu thiếu thông tin quan trọng khiến không thể đánh giá, điểm tối đa là 3.
- Nếu BĐS bị trùng hoặc dữ liệu rõ ràng lỗi, gắn cờ `invalid_candidate = true`.

Rubric theo persona:

| Persona | Điểm 5 cần thỏa |
|---|---|
| Family | Đủ phòng, trong ngân sách, gần trường/công viên, tiện ích sinh hoạt ổn |
| Young professional | Trong ngân sách, đi lại tiện, gần siêu thị/dịch vụ, diện tích vừa đủ |
| Investor | Giá/m2 tốt, vị trí có thanh khoản, gần đường lớn/tiện ích, ít outlier |
| Elderly | Gần bệnh viện/công viên, ít bất tiện di chuyển, môi trường tương đối yên tĩnh |
| Couple | Vừa ngân sách, tiện ích tốt, có dư địa cho nhu cầu tương lai |

## 6. Quy trình khảo sát và chấm nhãn

### Bước 1. Thu thập scenario

Dùng `survey/index.html` hoặc Google Form để thu:

- Nhu cầu tự nhiên bằng text.
- Ngân sách tối đa.
- Số phòng ngủ tối thiểu.
- Khu vực mong muốn nếu có.
- Mức quan trọng 1-5 cho các tiêu chí.
- Persona hoặc tình huống sống.

### Bước 2. Chuẩn hóa scenario

Chuyển câu trả lời survey thành `validation_user_scenarios.json`:

- Chuẩn hóa ngân sách về triệu VND.
- Chuẩn hóa persona.
- Tách hard constraints và soft preferences.
- Map tiêu chí text sang feature hệ thống hỗ trợ.

### Bước 3. Chạy solution

Với mỗi scenario:

- Chạy solution 2 lấy Top 10.
- Chạy solution 3 lấy Top 10.
- Lấy union candidate set.
- Xuất bảng chấm nhãn.

### Bước 4. Blind labeling

Khi đưa cho người chấm, nên ẩn solution/rank để giảm bias. Người chấm chỉ thấy:

- Nhu cầu người dùng.
- Thông tin BĐS.
- Các feature quan trọng.
- Không thấy BĐS này đến từ solution nào.

Thông tin nên hiển thị cho labeler:

```text
User need:
Gia đình 4 người, ngân sách dưới 6 tỷ, cần 3 phòng ngủ, ưu tiên trường và công viên.

Property:
ID: VAL_PROP_001
Giá: 5.8 tỷ
Diện tích: 62 m2
Phòng ngủ: 3
Quận: Gò Vấp
Gần trường nhất: 420m
Gần công viên nhất: 900m
Gần bệnh viện nhất: 1600m
Gần siêu thị nhất: 350m
Mô tả ngắn: ...

Label:
Relevance 1-5:
Reason:
```

### Bước 5. Tổng hợp nhãn

Nếu có 2-3 labeler:

```text
mean_relevance = average(labeler_scores)
median_relevance = median(labeler_scores)
binary_relevant = mean_relevance >= 4
```

Nên báo cáo thêm agreement:

| Metric | Cách dùng |
|---|---|
| Mean absolute disagreement | Trung bình độ lệch điểm giữa labeler |
| Exact agreement | Tỷ lệ labeler cho cùng điểm |
| Near agreement | Tỷ lệ điểm lệch không quá 1 |

Không nhất thiết phải dùng Cohen's Kappa nếu nhóm chưa quen; chỉ cần báo cáo agreement đơn giản cũng ổn.

## 7. Metrics dùng để so sánh solution 2 và Solution 3

### 7.1. Constraint Satisfaction Rate

Đo Top K có vi phạm điều kiện cứng không:

```text
CSR@K = số item Top K không vi phạm / K
```

Nên báo cáo:

```text
CSR@5
Hard constraint violation count
```

### 7.2. Average Relevance@K

Đo điểm phù hợp trung bình của Top K:

```text
AvgRel@K = mean(human_relevance của Top K)
```

Nên dùng:

```text
AvgRel@3
AvgRel@5
```

### 7.3. Precision@K

Chuyển relevance thành binary:

```text
relevant = mean_relevance >= 4
```

Sau đó:

```text
Precision@K = số item relevant trong Top K / K
```

### 7.4. NDCG@K

Dùng relevance 1-5 để đánh giá ranking có đưa item tốt lên cao không.

Nên báo cáo:

```text
NDCG@3
NDCG@5
```

### 7.5. MAP@K

Dùng khi đã có binary relevant:

```text
relevant = mean_relevance >= 4
```

MAP giúp đánh giá chất lượng ranking tổng thể qua nhiều scenario.

### 7.6. Pairwise Win Rate

Dễ hiểu khi trình bày với thầy:

```text
Nếu AvgRel@5 của solution 3 > solution 2 trong một scenario, Solution 3 thắng scenario đó.
```

Báo cáo:

```text
Solution 2 wins: x/30 scenarios
Solution 3 wins: y/30 scenarios
ties: z/30 scenarios
```

### 7.7. Stability / Sensitivity

Quan trọng riêng cho solution 3:

```text
Top-5 Stability = tỷ lệ item vẫn nằm trong Top 5 sau khi perturb trọng số 10-20%
```

Báo cáo:

- Top-5 Stability trung bình.
- Tiêu chí nhạy nhất.
- BĐS nào là robust top choice.

## 8. Cách chia validation theo mức thời gian

### Phương án tối thiểu

```text
10 scenarios
50-100 properties
10 candidates/scenario
2 labelers
100-200 label records
```

Dùng khi deadline rất gấp. Đủ để báo cáo có human-labeled validation nhỏ.

### Phương án khuyến nghị

```text
20-30 scenarios
100-300 properties
10-15 candidates/scenario
2-3 labelers
400-900 label records
```

Đây là mức nên hướng tới cho final.

### Phương án mạnh

```text
50 scenarios
500-1000 properties
15-20 candidates/scenario
3 labelers
2250-3000 label records
```

Chỉ nên làm nếu nhóm đủ thời gian và có tool chấm nhãn tốt.

## 9. Gợi ý bảng báo cáo validation trong final

### Dataset summary

| Thành phần | Số lượng |
|---|---:|
| Validation properties | 200 |
| User scenarios | 30 |
| Personas | 5 |
| Candidate pairs labeled | 450 |
| Labelers | 3 |
| Avg candidates/scenario | 15 |

### Label distribution

| Relevance score | Count | Percent |
|---:|---:|---:|
| 5 | 80 | 17.8% |
| 4 | 120 | 26.7% |
| 3 | 140 | 31.1% |
| 2 | 70 | 15.6% |
| 1 | 40 | 8.9% |

### Solution comparison

| Metric | Solution 2 | Solution 3 |
|---|---:|---:|
| CSR@5 | 96.7% | 98.0% |
| AvgRel@5 | 3.82 | 3.95 |
| Precision@5 | 68.0% | 72.0% |
| NDCG@5 | 0.841 | 0.867 |
| MAP@5 | 0.721 | 0.748 |
| Pairwise wins | 12/30 | 15/30 |
| Tie | 3/30 | 3/30 |

Các số trong bảng trên là ví dụ minh họa, không nên dùng làm kết quả thật nếu chưa chạy evaluation.

## 10. Fallback nếu không kịp khảo sát thật

Nếu không đủ thời gian lấy user thật, có thể dùng **semi-human validation**:

1. Nhóm tự tạo 20 persona/scenario.
2. Tạo candidate set từ Top 10 của Solution 2 và Solution 3.
3. Ít nhất 2 thành viên chấm nhãn độc lập theo rubric.
4. Báo cáo rõ đây là `manual-labeled validation`, không phải large-scale user study.

Cách viết trung thực trong báo cáo:

```text
Do chưa có public dataset chứa nhãn relevance cho bài toán tư vấn BĐS tại TP.HCM, nhóm xây dựng một tập validation thủ công gồm 20-30 user scenarios và các nhãn relevance 1-5 do 2-3 người đánh giá độc lập. Tập này được dùng để so sánh chất lượng ranking giữa các solution, bên cạnh synthetic validation dùng cho kiểm thử kỹ thuật.
```

## 11. Liên hệ với solution 2 và Solution 3

### Với solution 2

Validation cần kiểm tra:

- LLM parse nhu cầu đúng không.
- Nhu cầu tự nhiên có được map sang feature đo được không.
- Re-ranking sau enrichment có làm Top 5 phù hợp hơn không.
- Explanation có bám đúng dữ liệu không.

Metric thêm:

| Metric | Ý nghĩa |
|---|---|
| Intent parsing accuracy | LLM trích xuất đúng hard/soft preferences |
| Amenity mapping accuracy | Nhu cầu có map đúng sang POI/feature |
| Unsupported handling rate | Nhu cầu không đo được có bị gắn cờ đúng không |
| Explanation faithfulness | Lời giải thích có dựa trên feature thật không |

### Với solution 3

Validation cần kiểm tra:

- TOPSIS ranking có khớp human relevance không.
- Trọng số AHP/user preference có nhất quán không.
- Kết quả có ổn định khi trọng số thay đổi không.
- Tiêu chí nào ảnh hưởng mạnh nhất đến quyết định.

Metric thêm:

| Metric | Ý nghĩa |
|---|---|
| AHP Consistency Ratio | Độ nhất quán của preference |
| Top-5 Stability | Độ ổn định ranking khi thay đổi trọng số |
| Critical Criteria Count | Số tiêu chí làm ranking nhạy |
| Robust Top-1 Rate | Top 1 giữ nguyên trong bao nhiêu lần perturb |

## 12. Kết luận nên nói với thầy

Nên trình bày validation dataset như sau:

```text
Nhóm không tìm thấy public validation dataset có sẵn cho bài toán user preference -> real estate relevance tại TP.HCM. Vì vậy nhóm tự xây dựng validation dataset gồm ba phần: tập listing validation lấy từ dữ liệu BĐS công khai, tập user scenarios từ khảo sát/persona, và tập relevance labels do người đánh giá chấm độc lập. Cách này phù hợp với bài toán DSS vì chất lượng quyết định được đo bằng relevance, constraint satisfaction, ranking quality và sensitivity analysis thay vì accuracy đơn giản.
```
