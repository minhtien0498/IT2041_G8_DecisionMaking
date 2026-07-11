# Survey Plan for Validation Dataset

Tài liệu này mô tả cách dùng khảo sát để tạo validation dataset cho đề tài DSS tư vấn BĐS. Điểm quan trọng: khảo sát không chỉ để hỏi "người dùng muốn gì", mà còn để tạo **ground truth mềm** cho bài toán recommendation.

## 1. Khảo sát cần phục vụ mục tiêu gì

Nên tách khảo sát thành 2 lớp:

| Lớp khảo sát | Mục tiêu | Output |
|---|---|---|
| Preference survey | Thu nhu cầu thật của người dùng | `validation_user_scenarios.json` |
| Labeling survey | Chấm mức độ phù hợp của BĐS với từng nhu cầu | `user_preference_validation.json` |

Form hiện tại trong `survey/index.html` đang làm tốt phần đầu và một phần của phần sau:

- Thu persona.
- Thu ngân sách, số phòng, diện tích.
- Thu mức ưu tiên 1-5.
- Cho user chọn Top 5 BĐS họ thích.
- Xuất JSON.

Đã bổ sung thêm trường `user_need_text` để phục vụ solution 2, vì Solution 2 cần kiểm tra khả năng hiểu nhu cầu tự nhiên.

## 2. Vì sao không nên chỉ hỏi user chọn Top 5

Việc user chọn Top 5 là hữu ích, nhưng chưa đủ mạnh cho validation vì:

- Chỉ biết các căn được chọn, không biết các căn còn lại kém ở mức nào.
- Không có relevance score 1-5 nên NDCG/MAP ít giàu thông tin hơn.
- Nếu danh sách hiển thị đã bị lọc theo một logic nào đó, kết quả có thể bị bias.
- Không biết user chọn vì lý do gì.

Vì vậy, nên dùng form hiện tại để thu preference, sau đó làm thêm một bước labeling:

```text
Với mỗi user scenario
-> chạy solution 2 và Solution 1 lấy candidate set
-> đưa candidate set cho 2-3 người chấm relevance 1-5
```

## 3. Thiết kế Preference Survey

Preference survey là form dành cho người có nhu cầu mua/thuê nhà hoặc người đóng vai một persona cụ thể.

### Câu hỏi cần có

| Nhóm câu hỏi | Câu hỏi | Bắt buộc |
|---|---|---|
| Định danh | Họ tên hoặc mã ẩn danh | Có |
| Persona | Người trả lời thuộc nhóm nào | Có |
| Hard constraints | Ngân sách tối đa | Có |
| Hard constraints | Số phòng ngủ tối thiểu | Có |
| Hard constraints | Diện tích tối thiểu | Không |
| Natural language | Mô tả nhu cầu bằng lời | Nên có |
| Soft preferences | Giá hợp lý quan trọng mức nào | Có |
| Soft preferences | Gần trường học quan trọng mức nào | Có |
| Soft preferences | Gần công viên quan trọng mức nào | Có |
| Soft preferences | Gần bệnh viện quan trọng mức nào | Có |
| Soft preferences | Gần siêu thị/chợ quan trọng mức nào | Có |
| Soft preferences | Diện tích rộng quan trọng mức nào | Có |
| Soft preferences | Gần đường lớn quan trọng mức nào | Có |
| Choice | Chọn tối đa 5 BĐS thích nhất | Có nếu dùng form hiện tại |

### JSON output cần lưu

Form hiện tại xuất dữ liệu kiểu:

```json
{
  "response_id": "SURVEY_1781430000000",
  "timestamp": "2026-06-14T10:30:00.000Z",
  "respondent": "Anon_01",
  "user_type": "family",
  "hard_constraints": {
    "budget_max_billion": 6,
    "budget_max_million": 6000,
    "min_bedrooms": 3,
    "min_area_m2": 40
  },
  "user_need_text": "Gia đình có 2 con nhỏ, muốn nhà gần trường và công viên.",
  "preference_ratings": {
    "price": { "importance": 5, "weight": 0.2 },
    "school": { "importance": 5, "weight": 0.2 },
    "park": { "importance": 4, "weight": 0.16 }
  },
  "user_chosen_top5": ["GV_008", "GV_035", "GV_029"],
  "note": "Thứ tự trong user_chosen_top5 là thứ tự ưu tiên."
}
```

Nên lưu mỗi phản hồi thành một file:

```text
data/survey_responses/SURVEY_001.json
data/survey_responses/SURVEY_002.json
...
```

Sau đó gom lại thành:

```text
data/validation_user_scenarios.json
```

## 4. Thiết kế Labeling Survey

Labeling survey là bước quan trọng hơn nếu muốn có validation đúng nghĩa.

Người chấm sẽ nhận:

- Một user scenario.
- Một danh sách 10-15 BĐS ứng viên.
- Thông tin quan trọng của từng BĐS.
- Yêu cầu chấm relevance 1-5.

### Câu hỏi cho mỗi candidate

```text
Với nhu cầu trên, bạn đánh giá BĐS này phù hợp mức nào?

1 = Không phù hợp
2 = Ít phù hợp
3 = Tạm chấp nhận
4 = Phù hợp
5 = Rất phù hợp

Lý do ngắn:
```

### Thông tin BĐS nên hiển thị

| Field | Lý do |
|---|---|
| Giá | Kiểm tra ngân sách |
| Diện tích | Kiểm tra không gian |
| Số phòng ngủ | Kiểm tra hard constraints |
| Quận/phường | Kiểm tra vị trí |
| Khoảng cách trường | Quan trọng với family |
| Khoảng cách công viên | Quan trọng với family/elderly |
| Khoảng cách bệnh viện | Quan trọng với elderly |
| Khoảng cách siêu thị/chợ | Tiện ích sinh hoạt |
| Khoảng cách đường lớn | Di chuyển hoặc độ yên tĩnh |
| Mô tả ngắn | Bối cảnh phụ |

Không nên hiển thị:

- Solution nào đề xuất BĐS đó.
- Rank của solution.
- Điểm TOPSIS/LLM score.

Lý do: tránh bias người chấm.

## 5. Chọn người khảo sát

### Preference survey

Nên có 20-30 phản hồi, chia tương đối đều:

| Nhóm | Số phản hồi khuyến nghị |
|---|---:|
| Gia đình có con nhỏ | 6-8 |
| Người trẻ đi làm | 5-6 |
| Cặp đôi | 4-5 |
| Nhà đầu tư | 4-5 |
| Người cao tuổi/nghỉ hưu | 3-5 |

Nếu khó tìm người đúng persona, có thể cho người trả lời nhập theo vai:

```text
Hãy tưởng tượng bạn là một gia đình có 2 con nhỏ đang tìm nhà...
```

Nhưng trong báo cáo cần ghi rõ đây là persona-based survey, không phải khảo sát thị trường thực tế.

### Labeling survey

Nên có ít nhất 2 người chấm độc lập. Mức tốt hơn là 3 người chấm.

Người chấm có thể là:

- Thành viên nhóm, nhưng nên chấm độc lập.
- Bạn học không tham gia xây model.
- Người từng thuê/mua nhà hoặc có quan tâm BĐS.

## 6. Quy mô nên làm

### Bản tối thiểu

```text
10 user scenarios
10 candidates/scenario
2 labelers
= 200 label records
```

Dùng được nếu deadline gấp.

### Bản khuyến nghị

```text
20-30 user scenarios
10-15 candidates/scenario
2-3 labelers
= 400-1350 label records
```

Đây là mức hợp lý cho final.

### Bản mạnh

```text
50 user scenarios
15-20 candidates/scenario
3 labelers
= 2250-3000 label records
```

Chỉ nên làm nếu có tool chấm nhãn tốt.

## 7. Cách dùng khảo sát cho solution 2

Preference survey dùng để kiểm tra:

- LLM có parse đúng `user_need_text` không.
- LLM có tách đúng hard constraints và soft preferences không.
- LLM có map đúng nhu cầu sang amenity không.

Ví dụ:

```text
"Tôi có con nhỏ, muốn gần trường mẫu giáo và công viên"
```

Kỳ vọng parse:

```json
{
  "persona": "family",
  "hard_constraints": {},
  "soft_preferences": [
    {"feature": "distance_to_nearest_school_m", "direction": "lower_better"},
    {"feature": "distance_to_nearest_park_m", "direction": "lower_better"}
  ],
  "unsupported_requirements": []
}
```

Metric riêng cho Solution 2:

| Metric | Cách đo |
|---|---|
| Intent parsing accuracy | So sánh output LLM với label/rubric mong đợi |
| Amenity mapping accuracy | Nhu cầu có map đúng sang school/park/hospital/market không |
| Unsupported handling | Nhu cầu không đo được có bị gắn cờ đúng không |
| Explanation faithfulness | Lời giải thích có bám đúng feature thật không |

## 8. Cách dùng khảo sát cho solution 1

Preference survey dùng để tạo trọng số:

```text
importance 1-5 -> normalized user weights
```

Nếu muốn mạnh hơn, có thể thêm AHP pairwise survey, nhưng không bắt buộc nếu deadline gấp.

### Bản đơn giản

Dùng rating 1-5 hiện có:

```text
weight_i = importance_i / sum(importance)
```

### Bản nâng cao

Thêm 5-7 câu so sánh cặp:

```text
Với bạn, gần trường học quan trọng hơn giá cả bao nhiêu?
Với bạn, gần bệnh viện quan trọng hơn gần siêu thị bao nhiêu?
Với bạn, diện tích rộng quan trọng hơn gần đường lớn bao nhiêu?
```

Dùng thang AHP:

| Giá trị | Ý nghĩa |
|---:|---|
| 1 | Quan trọng như nhau |
| 3 | Quan trọng hơn nhẹ |
| 5 | Quan trọng hơn rõ |
| 7 | Quan trọng hơn rất nhiều |
| 9 | Quan trọng tuyệt đối |

Metric riêng cho Solution 1:

| Metric | Cách đo |
|---|---|
| AHP Consistency Ratio | Kiểm tra preference có mâu thuẫn không |
| Top-5 Stability | Ranking có ổn định khi weight thay đổi không |
| Human relevance / NDCG@5 | TOPSIS ranking có khớp người chấm không |
| Critical criteria | Tiêu chí nào làm ranking đổi nhiều nhất |

## 9. Cách chuyển survey response thành validation scenario

Mapping:

| Survey field | Validation field |
|---|---|
| `response_id` | `scenario_id` |
| `user_type` | `persona` |
| `user_need_text` | `user_need_text` |
| `hard_constraints.budget_max_million` | `hard_constraints.budget_max_million` |
| `hard_constraints.min_bedrooms` | `hard_constraints.min_bedrooms` |
| `hard_constraints.min_area_m2` | `hard_constraints.min_area_m2` |
| `preference_ratings` | `importance_1_to_5` and weights |
| `user_chosen_top5` | weak relevance / initial ranking signal |

`user_chosen_top5` có thể dùng như weak label:

```text
rank 1 -> relevance 5
rank 2 -> relevance 4
rank 3 -> relevance 4
rank 4 -> relevance 3
rank 5 -> relevance 3
not chosen -> unknown, không mặc định là 1
```

Lưu ý: không nên xem các BĐS không được chọn là "không phù hợp", vì user có thể chưa xem kỹ hoặc danh sách quá dài.

## 10. Điểm cần cải thiện của form hiện tại

Form hiện tại dùng được cho bản đầu tiên. Nếu còn thời gian, nên cải thiện:

| Cải thiện | Lý do |
|---|---|
| Thêm câu `user_need_text` | Đã thêm, phục vụ Solution 2 |
| Thêm khu vực mong muốn | Hữu ích khi mở rộng ngoài Gò Vấp |
| Cho rating từng BĐS 1-5 | Tạo relevance labels trực tiếp |
| Randomize thứ tự BĐS | Giảm bias do thứ tự hiển thị |
| Tách form label riêng | Blind labeling tốt hơn chọn Top 5 trực tiếp |
| Lưu tự động vào JSON/CSV | Tránh copy thủ công |

## 11. Cách viết trong báo cáo

Có thể viết:

```text
Nhóm thiết kế khảo sát gồm hai phần. Phần thứ nhất thu thập nhu cầu người dùng gồm persona, ngân sách, số phòng ngủ tối thiểu, mức độ ưu tiên các tiêu chí và mô tả nhu cầu tự nhiên. Phần này dùng để tạo user scenarios và trọng số tiêu chí cho các solution. Phần thứ hai dùng để chấm nhãn relevance 1-5 cho các cặp user scenario - property candidate. Các nhãn này được dùng làm ground truth mềm để tính AvgRel@5, Precision@5, NDCG@5, MAP@5 và so sánh solution 2 với solution 1.
```

Nếu chỉ kịp form hiện tại:

```text
Trong giai đoạn đầu, nhóm sử dụng khảo sát chọn Top 5 như weak-label validation. Thứ tự người dùng chọn được xem là tín hiệu ưu tiên ban đầu. Ở giai đoạn hoàn thiện, nhóm mở rộng sang relevance labeling 1-5 để đánh giá ranking chặt chẽ hơn.
```
