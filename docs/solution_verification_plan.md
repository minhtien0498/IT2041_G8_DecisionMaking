# Solution Verification Plan

File này trả lời câu hỏi:

```text
Với môn Hệ hỗ trợ ra quyết định dựa trên dữ liệu, làm sao kiểm chứng solution nào tốt hơn, đúng hơn, tối ưu hơn trong bài toán tư vấn BĐS?
```

Vấn đề chính: bài toán BĐS không có sẵn ground-truth kiểu "căn hộ A là lựa chọn đúng nhất cho user X". Vì vậy, nhóm cần tự xây dựng một cơ chế kiểm chứng có kiểm soát bằng **scenario-based validation** và **rubric chấm điểm**.

## 1. Nguyên tắc chung

Thay vì đánh giá bằng accuracy như bài toán classification, nhóm đánh giá recommendation theo:

- Recommendation có thỏa điều kiện bắt buộc không?
- Top 3/Top 5 có phù hợp persona không?
- Thứ hạng có hợp lý theo rubric không?
- Lời giải thích có bám đúng dữ liệu/điểm số không?
- Solution nào nhanh hơn, rẻ hơn, dễ mở rộng hơn?

## 2. Validation Dataset Đề Xuất

Tạo một tập validation nhỏ gồm:

```text
10-20 user scenarios/personas
100-200 property listings sạch
3-5 nhóm tiêu chí chấm điểm
```

Ví dụ file:

```text
real_estate_advisory/validation/user_scenarios.json
```

Mỗi scenario gồm:

```json
{
  "scenario_id": "family_01",
  "profile": "Gia đình 4 người, có 2 con nhỏ, ngân sách dưới 4 tỷ, ưu tiên gần trường học và công viên.",
  "hard_constraints": {
    "budget_max_vnd": 4000000000,
    "min_bedrooms": 2
  },
  "soft_preferences": {
    "distance_to_nearest_school_m": 0.30,
    "distance_to_nearest_park_m": 0.20,
    "distance_to_nearest_hospital_m": 0.15,
    "price_per_m2_score": 0.20,
    "supermarket_count_1km": 0.15
  }
}
```

## 3. Hướng A - Kiểm Chứng Bằng Rule-Based Rubric

### Ý tưởng

Tự định nghĩa rubric điểm cho từng persona. Mỗi BĐS được chấm điểm theo cùng công thức. Recommendation được xem là tốt nếu Top 5 đạt điểm cao và không vi phạm hard constraints.

### Cách làm

1. Tạo 10-20 persona.
2. Với mỗi persona, định nghĩa:
   - `hard_constraints`
   - `soft_preferences`
   - trọng số từng tiêu chí
3. Chạy từng solution trên cùng tập BĐS.
4. Tính điểm độc lập bằng rubric.
5. So sánh Top 5 của mỗi solution.

### Metric

| Metric | Cách tính |
|---|---|
| Constraint Satisfaction Rate | Tỷ lệ item trong Top 5 không vi phạm hard constraints |
| Average Top-5 Rubric Score | Trung bình điểm rubric của Top 5 |
| Best Item Rank | BĐS có điểm rubric cao nhất xuất hiện ở rank mấy |
| Top-3 Relevance | Trung bình điểm rubric của Top 3 |
| Ranking Consistency | Ranking của solution có tương quan với điểm rubric không |

### Ưu điểm

- Dễ làm.
- Minh bạch.
- Phù hợp DSS vì có rule và trọng số rõ.
- Không cần chuyên gia bên ngoài.

### Nhược điểm

- Rubric do nhóm tự thiết kế nên có tính chủ quan.
- Cần giải thích cơ sở chọn trọng số.

### Khi nào dùng

Đây là hướng nên dùng làm **evaluation chính cho midterm**.

## 4. Hướng B - Kiểm Chứng Bằng Persona-Based Manual Labeling

### Ý tưởng

Nhóm tạo persona, sau đó tự gán nhãn mức độ phù hợp cho một số cặp:

```text
(user scenario, property) -> relevance label
```

Ví dụ:

| Label | Ý nghĩa |
|---|---|
| 3 | Rất phù hợp |
| 2 | Phù hợp |
| 1 | Tạm được |
| 0 | Không phù hợp |

### Cách làm

1. Chọn 10 persona.
2. Chọn 100 property listing sạch.
3. Với mỗi persona, lấy 20-30 property ứng viên.
4. Nhóm chấm relevance label theo rubric.
5. Dùng các label này để đánh giá ranking.

### Metric

| Metric | Ý nghĩa |
|---|---|
| Precision@K | Trong Top K có bao nhiêu item relevant |
| NDCG@K | Ranking có đưa item relevant lên cao không |
| MAP@K | Chất lượng ranking trung bình |
| Relevance Agreement | Các thành viên có chấm giống nhau không |

### Ưu điểm

- Gần cách đánh giá recommender system hơn.
- Có thể trả lời câu hỏi "đúng hơn" bằng relevance label.
- Dễ trình bày với thầy nếu nhóm có bảng validation rõ.

### Nhược điểm

- Tốn công gán nhãn.
- Nhãn vẫn mang tính chủ quan.
- Cần ít nhất 2 người chấm để giảm bias nếu muốn nghiêm túc.

### Khi nào dùng

Dùng nếu nhóm muốn phần evaluation mạnh hơn rule-based rubric.

## 5. Hướng C - Kiểm Chứng Bằng Expert/Peer Review

### Ý tưởng

Đưa Top 5 recommendation của từng solution cho người đánh giá, có thể là:

- thành viên nhóm khác,
- bạn học,
- người có kinh nghiệm thuê/mua BĐS,
- hoặc thầy/cô nếu phù hợp.

Người đánh giá chọn ranking nào hợp lý hơn mà không biết đó là solution nào.

### Cách làm

1. Với mỗi persona, chạy Solution 1 và Solution 2.
2. Ẩn tên solution, chỉ hiển thị:
   - profile user,
   - Top 5 BĐS,
   - lý do gợi ý.
3. Người đánh giá chọn:
   - ranking nào phù hợp hơn,
   - explanation nào thuyết phục hơn,
   - có lỗi nào nghiêm trọng không.

### Metric

| Metric | Ý nghĩa |
|---|---|
| Pairwise Win Rate | Solution nào được chọn nhiều hơn |
| Explanation Preference Rate | Explanation nào được đánh giá tốt hơn |
| Serious Error Count | Số lỗi vi phạm yêu cầu bắt buộc |
| Usefulness Score | Người đánh giá cho điểm hữu ích 1-5 |

### Ưu điểm

- Gần với trải nghiệm người dùng thật.
- Đánh giá được yếu tố mềm như lời giải thích, độ thuyết phục.
- Dễ dùng để bổ sung cho evaluation định lượng.

### Nhược điểm

- Tốn người đánh giá.
- Khó kiểm soát bias.
- Không đủ chặt nếu dùng làm metric duy nhất.

### Khi nào dùng

Dùng làm **evaluation phụ** để chứng minh solution 2 có trải nghiệm tốt hơn.

## 6. Hướng D - Kiểm Chứng Bằng Constraint Stress Test

### Ý tưởng

Tạo các input khó để kiểm tra hệ thống có giữ đúng luật không.

Ví dụ:

- Ngân sách quá thấp.
- Yêu cầu nhiều phòng ngủ nhưng diện tích nhỏ.
- Muốn gần trường nhưng xa trung tâm.
- Muốn gần bệnh viện nhưng tránh khu đông đúc.
- Nhập nhu cầu mơ hồ bằng ngôn ngữ tự nhiên.

### Cách làm

1. Tạo 10 test case đặc biệt.
2. Chạy cả 2 solution.
3. Kiểm tra:
   - có vi phạm hard constraints không,
   - có trả về rỗng khi không có lựa chọn phù hợp không,
   - LLM có bịa lý do không,
   - hệ thống có giải thích trade-off không.

### Metric

| Metric | Ý nghĩa |
|---|---|
| Hard Constraint Violation Count | Số recommendation vi phạm điều kiện bắt buộc |
| Unsupported Requirement Handling | Có nhận diện nhu cầu không hỗ trợ không |
| Empty Result Handling | Có xử lý trường hợp không có BĐS phù hợp không |
| Trade-off Explanation Score | Có giải thích đánh đổi không |

### Ưu điểm

- Rất hợp để test độ tin cậy của DSS.
- Dễ phát hiện lỗi nghiêm trọng.
- Cho thấy hệ thống không chỉ hoạt động ở case đẹp.

### Nhược điểm

- Không thay thế được đánh giá ranking.
- Cần thiết kế test case kỹ.

### Khi nào dùng

Dùng để kiểm chứng robustness và safety của solution.

## 7. Hướng E - Kiểm Chứng Chi Phí, Độ Trễ, Khả Năng Triển Khai

### Ý tưởng

Không phải solution tốt nhất về độ phù hợp luôn là solution tốt nhất tổng thể. Với DSS thực tế, cần cân bằng:

- độ phù hợp,
- chi phí,
- tốc độ,
- khả năng mở rộng.

### Metric

| Metric | Solution 1 kỳ vọng | Solution 2 kỳ vọng |
|---|---|---|
| Latency | Thấp | Cao hơn |
| API cost | Thấp | Cao hơn |
| Implementation complexity | Thấp | Cao |
| Interpretability | Cao | Trung bình-cao |
| Personalization | Trung bình | Cao |
| Scalability | Cao nếu precompute | Phụ thuộc API/cache |

### Khi nào dùng

Dùng để giải thích vì sao nhóm giữ cả 2 solution:

- Solution 1 tối ưu về chi phí, tốc độ, ổn định.
- Solution 2 tối ưu về cá nhân hóa và xử lý nhu cầu tự nhiên.

## 8. So Sánh Solution 1 và Solution 2

| Tiêu chí | Solution 1 | Solution 2 |
|---|---|---|
| Constraint satisfaction | Cao | Cao nếu LLM parse đúng |
| Top-K relevance | Tốt với nhu cầu có trong form | Tốt hơn nếu user có nhu cầu tự nhiên |
| Explainability | Cao, do điểm số rõ | Cao nếu LLM bám đúng score |
| Flexibility | Thấp | Cao |
| Latency | Thấp | Cao hơn |
| API cost | Thấp | Cao hơn |
| Risk | Thấp | Trung bình |
| Phù hợp midterm | Rất cao | Trung bình-cao |
| Phù hợp final | Trung bình | Cao |

## 9. Đề Xuất Evaluation Chính Thức Cho Nhóm

Nên dùng bộ evaluation kết hợp:

```text
Primary: Rule-based rubric evaluation
Secondary: Constraint stress test
Optional: Peer review / pairwise comparison
Operational: latency + cost + complexity
```

Pipeline evaluation:

```text
User scenarios
      |
      v
Run Solution 1 and Solution 2
      |
      v
Collect Top 5 recommendations
      |
      v
Apply rubric scoring
      |
      v
Check hard constraint violations
      |
      v
Compare relevance, explanation, latency, cost
```

## 10. Câu Trả Lời Ngắn Cho Thầy

Có thể trả lời:

```text
Vì bài toán tư vấn BĐS không có ground-truth trực tiếp như bài toán phân loại, nhóm sẽ xây dựng một tập validation theo kịch bản người dùng. Mỗi kịch bản gồm hard constraints và soft preferences có trọng số. Hai solution sẽ chạy trên cùng một tập BĐS, sau đó được so sánh bằng constraint satisfaction, Top-K relevance theo rubric, ranking quality, explanation faithfulness, latency và cost. Như vậy, nhóm vẫn có cơ chế kiểm chứng solution nào phù hợp hơn, ổn định hơn và khả thi hơn.
```

## 11. Slide Gợi Ý

### Slide: Solution Verification

Bullet points:

- Real-estate recommendation has no direct ground-truth label.
- We build scenario-based validation with 10-20 user personas.
- Each persona has hard constraints and weighted soft preferences.
- Both solutions run on the same property subset.
- Compare: constraint satisfaction, Top-K relevance, ranking quality, explanation faithfulness, latency, cost.

### Slide: Evaluation Matrix

| Metric | Why it matters |
|---|---|
| Constraint satisfaction | Không recommend căn vi phạm ngân sách/số phòng |
| Top-K relevance | Top 3/Top 5 có hợp nhu cầu không |
| Explanation faithfulness | LLM có giải thích đúng theo dữ liệu không |
| Latency/cost | Có khả thi khi triển khai không |

