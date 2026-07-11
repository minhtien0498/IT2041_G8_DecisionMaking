# Chi tiết Solution 1

> Ghi chú cập nhật `2026-07-11`:
> `Solution 1` hiện tại là hướng **MCDA/TOPSIS** của `Phú`, được đổi tên từ `Solution 3` cũ.
> Hướng rule-based `Solution 1` cũ đã bị loại khỏi scope final và không còn là tài liệu active nữa.

## Data-driven MCDA: AHP/Entropy Weights + TOPSIS Ranking + Sensitivity Analysis

Do hướng rule-based cũ có rủi ro bị xem là bộ lọc/recommender thông thường, `Solution 1` hiện tại chuyển trọng tâm sang một mô hình **ra quyết định đa tiêu chí** rõ hơn. Hướng đề xuất là:

```text
User Preference + Enriched Property Data
-> Decision Matrix
-> AHP/Entropy Weighting
-> TOPSIS Ranking
-> Sensitivity Analysis
-> Top 5 + Trade-off Explanation
```

Ý tưởng chính: mỗi bất động sản là một phương án quyết định, mỗi thuộc tính là một tiêu chí quyết định. Hệ thống không chỉ lọc và cộng điểm, mà xây dựng một ma trận ra quyết định, chuẩn hóa tiêu chí lợi ích/chi phí, tính trọng số có cơ sở, so sánh từng phương án với nghiệm lý tưởng và phân tích độ ổn định của kết quả.

## Vì sao phù hợp hơn với môn DSS with Data

`Solution 1` hiện tại phù hợp hơn hướng rule-based cũ vì có đủ các thành phần cốt lõi của DSS:

- **Alternatives**: các bất động sản ứng viên.
- **Criteria**: giá, diện tích, số phòng, giá/m2, khoảng cách đến trường, công viên, bệnh viện, siêu thị, giao thông.
- **Decision matrix**: bảng phương án x tiêu chí.
- **Preference model**: trọng số tiêu chí từ người dùng hoặc từ dữ liệu.
- **Decision method**: TOPSIS để xếp hạng phương án theo khoảng cách đến nghiệm lý tưởng.
- **Sensitivity analysis**: kiểm tra nếu trọng số thay đổi thì Top 5 có ổn định không.
- **Explanation**: giải thích trade-off giữa các phương án.

Điểm khác biệt quan trọng với hướng rule-based cũ:

| Nội dung | Solution 1 cũ | Solution 1 hiện tại |
|---|---|---|
| Bản chất | Rule/filter + weighted score | Multi-Criteria Decision Analysis |
| Trọng số | Nhóm tự đặt hoặc form cố định | AHP từ preference người dùng + Entropy/CRITIC từ dữ liệu |
| Cách xếp hạng | Cộng điểm tuyến tính | So sánh với ideal best và ideal worst |
| Kiểm chứng | Chủ yếu constraint/rule consistency | NDCG, relevance, stability, sensitivity |
| Tính DSS | Yếu, dễ giống bộ lọc nâng cao | Mạnh hơn, đúng bài toán hỗ trợ ra quyết định |

## Bước 1. Xây dựng decision matrix

Từ tập dữ liệu BĐS đã enrich, tạo ma trận:

```text
Rows    = properties
Columns = decision criteria
```

Ví dụ tiêu chí:

| Criteria | Type | Meaning |
|---|---|---|
| `price_million_vnd` | cost | Giá càng thấp càng tốt |
| `price_per_m2_million` | cost | Giá/m2 càng thấp càng tốt |
| `area_m2` | benefit | Diện tích càng lớn càng tốt |
| `bedrooms` | benefit | Số phòng ngủ càng nhiều càng tốt |
| `distance_to_nearest_school_m` | cost | Gần trường hơn thì tốt hơn |
| `distance_to_nearest_park_m` | cost | Gần công viên hơn thì tốt hơn |
| `distance_to_nearest_hospital_m` | cost | Gần bệnh viện hơn thì tốt hơn |
| `distance_to_nearest_supermarket_m` | cost | Gần siêu thị/chợ hơn thì tốt hơn |
| `distance_to_nearest_boulevard_m` | cost/benefit | Tùy persona: cần tiện đi lại thì cost, cần yên tĩnh thì benefit |

Hard constraints vẫn được dùng, nhưng chỉ để loại các phương án chắc chắn không phù hợp:

```text
price <= budget_max
bedrooms >= min_bedrooms
district in preferred_districts, nếu có
```

Sau khi lọc cứng, TOPSIS xử lý phần ra quyết định mềm.

## Bước 2. Tính trọng số bằng AHP hoặc preference survey

Thay vì tự đặt trọng số trực tiếp, hệ thống có thể hỏi người dùng hoặc dùng khảo sát để tạo ma trận so sánh cặp tiêu chí.

Ví dụ với persona gia đình:

```text
Gần trường quan trọng hơn giá bao nhiêu lần?
Gần công viên quan trọng hơn diện tích bao nhiêu lần?
Giá quan trọng hơn gần siêu thị bao nhiêu lần?
```

Từ pairwise comparison matrix, AHP sinh ra trọng số:

```json
{
  "price_million_vnd": 0.25,
  "area_m2": 0.12,
  "bedrooms": 0.10,
  "distance_to_nearest_school_m": 0.28,
  "distance_to_nearest_park_m": 0.15,
  "distance_to_nearest_supermarket_m": 0.10
}
```

AHP còn có **Consistency Ratio (CR)**. Nếu CR quá cao, hệ thống biết preference của người dùng đang mâu thuẫn và có thể yêu cầu điều chỉnh hoặc ghi nhận uncertainty.

Ngưỡng thường dùng:

```text
CR <= 0.10: preference tương đối nhất quán
CR > 0.10: preference có mâu thuẫn, cần xem lại
```

## Bước 3. Tính trọng số khách quan từ dữ liệu

Để làm rõ yếu tố "with Data", có thể kết hợp thêm trọng số khách quan từ dữ liệu bằng Entropy Weighting hoặc CRITIC.

Ý nghĩa:

- Nếu một tiêu chí gần như không phân biệt được các BĐS, trọng số dữ liệu của nó thấp.
- Nếu một tiêu chí có độ biến thiên cao và giúp phân biệt phương án tốt/xấu, trọng số dữ liệu của nó cao hơn.

Công thức kết hợp:

```text
final_weight = alpha * user_weight + (1 - alpha) * data_weight
```

Ví dụ:

```text
alpha = 0.7
```

Nghĩa là preference người dùng vẫn là chính, nhưng dữ liệu thực tế có ảnh hưởng 30%.

Đây là điểm giúp `Solution 1` hiện tại khác với hướng rule-based cũ: trọng số không chỉ là ý kiến chủ quan, mà được hiệu chỉnh bằng đặc điểm của dataset.

## Bước 4. TOPSIS ranking

TOPSIS xếp hạng phương án theo nguyên tắc:

```text
Phương án tốt nên gần nghiệm lý tưởng tốt nhất và xa nghiệm lý tưởng xấu nhất.
```

Quy trình:

1. Chuẩn hóa decision matrix.
2. Nhân với trọng số tiêu chí.
3. Xác định ideal best:
   - tiêu chí benefit: giá trị lớn nhất.
   - tiêu chí cost: giá trị nhỏ nhất.
4. Xác định ideal worst:
   - tiêu chí benefit: giá trị nhỏ nhất.
   - tiêu chí cost: giá trị lớn nhất.
5. Tính khoảng cách từng BĐS đến ideal best và ideal worst.
6. Tính closeness coefficient:

```text
C_i = D_i_minus / (D_i_plus + D_i_minus)
```

Trong đó:

- `D_i_plus`: khoảng cách đến ideal best.
- `D_i_minus`: khoảng cách đến ideal worst.
- `C_i` càng cao thì phương án càng tốt.

Output của mỗi BĐS:

```json
{
  "property_id": "GV_008",
  "topsis_score": 0.782,
  "rank": 1,
  "distance_to_ideal_best": 0.18,
  "distance_to_ideal_worst": 0.64,
  "strengths": ["gần trường", "giá trong ngân sách", "diện tích tốt"],
  "tradeoffs": ["xa công viên hơn lựa chọn hạng 2"]
}
```

## Bước 5. Sensitivity analysis

Sau khi có Top 5, hệ thống kiểm tra độ ổn định của quyết định:

```text
Nếu tăng/giảm trọng số mỗi tiêu chí 10-20%, Top 5 có thay đổi mạnh không?
```

Metric đề xuất:

| Metric | Ý nghĩa |
|---|---|
| Top-5 Stability | Tỷ lệ BĐS vẫn nằm trong Top 5 sau khi nhiễu trọng số |
| Rank Change Average | Trung bình mức thay đổi thứ hạng |
| Critical Criteria | Tiêu chí nào làm ranking đổi nhiều nhất |
| Robust Winner | BĐS nào vẫn giữ Top 1 trong đa số lần thử |

Đây là phần rất "DSS": hệ thống không chỉ đưa ra đáp án, mà còn nói đáp án đó có ổn định hay nhạy với giả định nào.

## Bước 6. LLM explanation

LLM không quyết định ranking. LLM chỉ nhận:

- Top 5 từ TOPSIS.
- Trọng số tiêu chí.
- Điểm từng tiêu chí.
- Kết quả sensitivity analysis.
- Trade-off giữa các phương án.

LLM sinh giải thích:

```text
Căn GV_008 đứng hạng 1 vì gần trường và giá nằm tốt trong ngân sách. Tuy nhiên, nếu người dùng tăng mạnh trọng số công viên, căn GV_035 có thể vượt lên do gần công viên hơn. Điều này cho thấy lựa chọn GV_008 tốt nhất khi ưu tiên chính là trường học và ngân sách.
```

## Pipeline đề xuất

```text
User Input / Survey Preference
-> Hard Constraint Filtering
-> Build Decision Matrix
-> AHP User Weighting
-> Entropy/CRITIC Data Weighting
-> Combine Weights
-> TOPSIS Ranking
-> Sensitivity Analysis
-> Top 5 Recommendation
-> LLM Trade-off Explanation
```

## Validation cho Solution 1

Có thể đánh giá bằng:

| Metric | Ý nghĩa |
|---|---|
| Constraint Satisfaction Rate | Top 5 có vi phạm điều kiện bắt buộc không |
| Average Human Relevance | Điểm phù hợp trung bình do người chấm đánh giá |
| NDCG@5 | Phương án người đánh giá thích có được đưa lên cao không |
| MAP@5 | Chất lượng ranking tổng thể |
| Top-5 Stability | Ranking có ổn định khi trọng số thay đổi không |
| AHP Consistency Ratio | Preference người dùng có nhất quán không |

Nếu chưa có survey lớn, có thể dùng tối thiểu:

```text
10-20 scenarios
Top 10 candidate properties mỗi scenario
2 labelers chấm relevance 1-5
```

Protocol chi tiết cho tập validation nằm ở:

```text
docs/validation_dataset_plan.md
```

Với `Solution 1`, phần validation nên nhấn mạnh thêm:

- Human relevance để kiểm tra TOPSIS ranking có khớp đánh giá người dùng không.
- Top-5 Stability để kiểm tra ranking có ổn định khi trọng số thay đổi không.
- AHP Consistency Ratio để kiểm tra preference người dùng có mâu thuẫn không.
- Critical Criteria để biết tiêu chí nào làm quyết định nhạy nhất.

## Khi nào chọn Solution 1

Nên chọn `Solution 1` hiện tại làm hướng final nếu nhóm cần một phương án:

- Không phụ thuộc quá nhiều vào LLM.
- Không cần API phức tạp như Solution 2.
- Có nền tảng DSS rõ ràng.
- Có thể giải thích bằng mô hình ra quyết định đa tiêu chí.
- Dễ so sánh với Solution 2 trong final report.

Tóm lại:

```text
Solution 2 = LLM + dynamic data enrichment + re-ranking
Solution 1 = MCDA/TOPSIS + data-driven weighting + sensitivity analysis
```

Hai solution này đủ khác nhau và đều hợp với DSS with Data hơn hướng rule-based cũ.
