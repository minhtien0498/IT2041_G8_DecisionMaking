# Chi tiết Solution 5.1

## Form -> Inference Engine -> LLM explaination

Quy trình đề xuất:
1. Người dùng nhập nhu cầu theo form cố định.
2. Hệ thống chuẩn hóa input thành một `user preference profile` gồm:
   - `hard constraints`: điều kiện bắt buộc phải thỏa mãn.
   - `soft preferences`: tiêu chí dùng để chấm điểm mức độ phù hợp.
   - `weight`: trọng số cho từng tiêu chí.
   - `preference direction`: mong muốn nhỏ hơn, lớn hơn, hay nằm trong một khoảng.
3. Inference engine xử lý theo 2 tầng:
   - `rule-based filtering`: loại bỏ các bất động sản không thỏa điều kiện bắt buộc.
   - `rule-based scoring`: chấm điểm các bất động sản còn lại theo từng tiêu chí.
4. Hệ thống thực hiện sắp xếp theo `total_score` và lấy Top 5.
5. LLM chỉ nhận Top 5 cùng các bằng chứng chấm điểm để sinh lời giải thích tự nhiên, không tự quyết định xếp hạng.

Ý chính cần nhấn mạnh: inference engine trong solution 5.1 không chỉ làm lọc, mà còn phải tạo ra cấu trúc điểm có thể kiểm chứng được. LLM là lớp giải thích cuối cùng, không phải lớp suy luận chính.

### Bước 1. Chuẩn hóa form thành hồ sơ nhu cầu
Ví dụ một form có thể sinh ra cấu trúc trung gian như sau:
- `budget_max = 3.5` tỷ
- `min_bedroom = 3`
- `preferred_school_distance <= 1000m`
- `preferred_park_distance <= 1500m`
- `prefer_far_from_boulevard = true`
- `weights = {price: 0.30, bedroom: 0.20, school: 0.20, park: 0.10, boulevard: 0.20}`

Từ đó hệ thống tách thành:
- `hard constraints`: ví dụ `price <= budget_max`, `bedroom >= min_bedroom`
- `soft preferences`: ví dụ càng gần trường càng tốt, càng gần công viên càng tốt, càng xa đại lộ càng tốt

### Bước 2. Rule-based filtering
Đây là phần inference engine ở mức luật cứng. Mục tiêu là giảm không gian tìm kiếm và đảm bảo các gợi ý không vi phạm nhu cầu tối thiểu.

Ví dụ luật:
- Nếu `price > budget_max` thì loại.
- Nếu `number_of_room < min_bedroom` thì loại.
- Nếu người dùng khai có con đang đi học và chọn ưu tiên mạnh cho trường học, có thể đặt thêm luật cứng: nếu `distance_to_nearest_high_school > threshold` thì loại.

Kết quả của bước này là một tập ứng viên hợp lệ, ví dụ từ 1000 bất động sản còn lại 80 bất động sản.

### Bước 3. Rule-based scoring
Với các ứng viên còn lại, hệ thống chấm điểm theo từng thuộc tính. Mỗi thuộc tính nên có:
- `raw value`: giá trị thực tế của bất động sản
- `normalized_score`: điểm chuẩn hóa trong khoảng `[0, 1]`
- `weight`: trọng số tiêu chí
- `contribution_score = normalized_score * weight`

Công thức tổng quát:

`total_score = sum(contribution_score_i)`

Ba kiểu tiêu chí phổ biến:
1. Càng nhỏ càng tốt, ví dụ `price`, `distance_to_nearest_school`, `distance_to_nearest_park`
2. Càng lớn càng tốt, ví dụ `number_of_room`
3. Càng xa càng tốt trong một số trường hợp đặc biệt, ví dụ `distance_to_nearest_boulevard`

Ví dụ chuẩn hóa:
- Với tiêu chí càng nhỏ càng tốt:
  `normalized_score = max(0, min(1, (threshold_max - value) / (threshold_max - threshold_min)))`
- Với tiêu chí càng lớn càng tốt:
  `normalized_score = max(0, min(1, (value - threshold_min) / (threshold_max - threshold_min)))`

Ví dụ:
- Giá ngân sách tối đa 3.5 tỷ, căn hộ giá 3.0 tỷ thì được điểm cao.
- Khoảng cách đến trường 500m sẽ được điểm cao hơn 1200m.
- Khoảng cách đến đại lộ 3000m sẽ được điểm cao hơn 1000m nếu người dùng muốn ở xa trục giao thông lớn.

### Bước 4. Output từ inference engine cho LLM
Response bạn đang nghĩ tới là đúng hướng, nhưng nên bổ sung thêm ngữ nghĩa để LLM giải thích đúng và nhất quán. Mỗi thuộc tính nên có:
- `value`
- `unit`
- `preference_type`
- `weight`
- `normalized_score`
- `contribution_score`

Ví dụ cấu trúc tốt hơn:

```python
bds_recommendation = [
    {
        "name": "Chung cu ABC",
        "total_score": 0.84,
        "attributes": {
            "number_of_room": {
                "value": 3,
                "unit": "room",
                "preference_type": "higher_better",
                "weight": 0.20,
                "normalized_score": 1.00,
                "contribution_score": 0.20
            },
            "distance_to_nearest_high_school": {
                "value": 500,
                "unit": "meter",
                "preference_type": "lower_better",
                "weight": 0.20,
                "normalized_score": 0.90,
                "contribution_score": 0.18
            },
            "distance_to_nearest_park": {
                "value": 1000,
                "unit": "meter",
                "preference_type": "lower_better",
                "weight": 0.10,
                "normalized_score": 0.60,
                "contribution_score": 0.06
            },
            "price": {
                "value": 3000,
                "unit": "million_vnd",
                "preference_type": "lower_better",
                "weight": 0.30,
                "normalized_score": 0.90,
                "contribution_score": 0.27
            },
            "distance_to_nearest_boulevard": {
                "value": 3000,
                "unit": "meter",
                "preference_type": "higher_better",
                "weight": 0.20,
                "normalized_score": 0.65,
                "contribution_score": 0.13
            }
        }
    }
]
```

Lợi ích của cấu trúc này là LLM có thể giải thích theo đúng logic hệ thống, ví dụ: căn hộ được xếp hạng cao vì giá phù hợp ngân sách, đủ số phòng ngủ, gần trường học và ở tương đối xa đại lộ.

### Bước 5. Vai trò cụ thể của LLM
LLM không nên tự tính điểm từ đầu. LLM chỉ nên:
- diễn giải vì sao bất động sản A đứng trên B
- tóm tắt các điểm mạnh và điểm yếu của từng phương án
- cá nhân hóa lời giải thích theo hồ sơ người dùng

Nói cách khác, pipeline của solution 5.1 nên được mô tả là:

`Form -> Preference Profile -> Rule-based Filtering -> Rule-based Scoring -> Top 5 Candidates -> LLM Explanation`

Nếu viết vào báo cáo, có thể chốt phần này bằng nhận định sau: solution 5.1 phù hợp khi bài toán có bộ tiêu chí tương đối cố định, dễ biểu diễn bằng form, và cần đảm bảo tính minh bạch trong quá trình xếp hạng.