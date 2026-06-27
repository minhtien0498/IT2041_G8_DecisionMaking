# Chi tiết Solution 2

## Form + User Query -> Inference Engine + LLM -> LLM explaination

Ý tưởng cốt lõi của Solution 2 là giữ lại phần form cố định của Solution 1 để hệ thống có một khung tiêu chí ổn định, sau đó dùng LLM để xử lý phần nhu cầu bổ sung bằng ngôn ngữ tự nhiên. Theo cách này, LLM không thay thế inference engine mà đóng vai trò mở rộng phạm vi tiêu chí mà hệ thống có thể hiểu và đo lường.

### Bước 1. Hybrid input từ người dùng
Input gồm 2 phần:
1. `form cố định`: giống Solution 1, dùng để thu thập các tiêu chí cơ bản như ngân sách, số phòng, khoảng cách đến trường học, công viên, trục giao thông. Phần này giúp người dùng không bị mơ hồ khi sử dụng hệ thống, đồng thời đảm bảo hệ thống hoạt động trơn tru kể cả với những nhu cầu bất khả thi.
2. `nhu cầu thêm`: phần người dùng nhập tự do để mô tả các mong muốn đặc biệt mà rule-based hiện tại chưa có, chưa aware hoặc còn quá mơ hồ.

Ví dụ:
- "Càng nhiều chợ xung quanh càng tốt"
- "Ưu tiên nơi có nhiều tiện ích trong bán kính 1 km"
- "Muốn gần khu đông dân cư để tiện sinh hoạt"

Phần 1 giúp giữ trải nghiệm sử dụng ổn định. Phần 2 giúp tăng độ linh hoạt của hệ thống.

### Bước 2. LLM reasoning cho phần nhu cầu thêm
LLM phân tích `nhu cầu thêm` và tách chúng thành ba nhóm:
- `hard constraints`: điều kiện bắt buộc, nếu đo lường được thì sẽ dùng để loại ứng viên.
- `soft preferences`: tiêu chí ưu tiên, dùng để chấm điểm bổ sung.
- `unsupported requirements`: nhu cầu không thể đo lường bằng dữ liệu và tool hiện có thì sẽ bị loại bỏ hoặc gắn cờ là chưa hỗ trợ.

Ngoài ra, LLM cũng phải xử lý các nhu cầu bị `duplicate` với form. Trong thực tế, người dùng có thể nhập lại một tiêu chí cũ ở phần tự do để nhấn mạnh hoặc diễn đạt rõ hơn cho mục đích giải thích. Khi đó hệ thống không nên bỏ qua hoàn toàn, mà cần:
- nhận diện nhu cầu đó đã tồn tại trong form
- hợp nhất với tiêu chí cũ thay vì tạo một thuộc tính mới trùng lặp
- cập nhật lại mức ưu tiên hoặc mô tả ngữ nghĩa nếu phần nhập tự do làm rõ thêm mong muốn của người dùng

Điểm quan trọng ở bước này là `capability-aware reasoning`: LLM chỉ được phép giữ lại những nhu cầu có thể chuyển thành thuộc tính đo lường được bằng tool hiện có.

Hiện tại hệ thống có 2 tool chính:
- lấy `lat, long` từ địa chỉ bất động sản
- tìm tiện ích xung quanh bằng Search Map API từ `lat, long` và `tên tiện ích`

Vì vậy, trước khi enrichment, LLM phải quy đổi từ `tên nhu cầu` sang `tên tiện ích` mà tool có thể hiểu. Ví dụ:
- "Càng nhiều chợ xung quanh càng tốt" -> amenity name: `market`
- "Ưu tiên gần trường mẫu giáo" -> amenity name: `kindergarten`
- "Muốn nhiều quán cafe quanh nhà" -> amenity name: `cafe`

Chỉ khi quy đổi được sang `amenity name` thì hệ thống mới có thể gọi Search Map API một cách nhất quán cho tất cả ứng viên.

Vì vậy, Solution 2 phù hợp với các nhu cầu có thể quy đổi thành đặc trưng không gian như:
- số lượng chợ trong bán kính xác định
- khoảng cách đến tiện ích gần nhất
- mật độ tiện ích xung quanh

Ngược lại, các nhu cầu quá chủ quan như "hàng xóm thân thiện" hoặc "khu vực có vibe tốt" sẽ không nên đưa vào scoring nếu không có nguồn dữ liệu tương ứng.

### Bước 3. Chạy form qua inference engine để lấy Top 10 ban đầu
Phần `form cố định` được xử lý giống Solution 1:
- chuẩn hóa thành `hard constraints` và `soft preferences`
- `rule-based filtering`
- `rule-based scoring`
- lấy `Top 10` thay vì `Top 5`

Lý do lấy Top 10 là để tạo vùng đệm trước bước tái chấm điểm. Một số tiêu chí mới ở phần `nhu cầu thêm` có thể làm thay đổi thứ hạng mạnh, ví dụ một bất động sản đang đứng thứ 6 theo form có thể trở thành thứ 1 sau khi bổ sung tiêu chí "nhiều chợ xung quanh". Nếu chỉ giữ Top 5 quá sớm thì có thể làm mất ứng viên tốt.

### Bước 4. Enrichment bằng tool cho Top 10
Với từng bất động sản trong Top 10, hệ thống thực hiện cùng một quy trình enrichment để đảm bảo tất cả ứng viên có cùng tập thuộc tính mới:
1. dùng địa chỉ để lấy `lat, long`
2. dùng kết quả từ bước 2 để lấy `amenity name` tương ứng với từng nhu cầu bổ sung
3. gọi Search Map API với `lat, long + amenity name`
4. sinh thêm các thuộc tính mới cho tất cả 10 ứng viên

Ví dụ ánh xạ từ câu truy vấn sang thuộc tính:
- "Càng nhiều chợ xung quanh càng tốt" -> amenity name: `market` -> `nearby_market_count_within_1km`
- "Ưu tiên gần trường mẫu giáo" -> amenity name: `kindergarten` -> `distance_to_nearest_kindergarten`
- "Muốn nhiều quán cafe quanh nhà" -> amenity name: `cafe` -> `nearby_cafe_count_within_500m`

Nguyên tắc quan trọng là nếu một thuộc tính mới được tạo ra cho một ứng viên thì phải được tạo cho toàn bộ Top 10, để quá trình scoring và so sánh là đồng nhất.

### Bước 5. Post-filtering, re-scoring và re-ranking
Sau khi enrichment, hệ thống thực hiện một vòng đánh giá mới:
1. `post-filtering`: áp dụng các `hard constraints` mới nếu chúng đo lường được sau enrichment.
2. `additional scoring`: chấm điểm các `soft preferences` mới sinh ra từ phần nhu cầu thêm.
3. `normalization`: chuẩn hóa toàn bộ điểm về khoảng `[0, 1]`.
4. `re-ranking`: tính lại `total_score` cuối cùng và sắp xếp lại thứ hạng.

Một cách kết hợp đơn giản và minh bạch là:

`final_score = alpha * base_score + beta * additional_score`

Trong đó:
- `base_score`: điểm từ form cố định ở Solution 1
- `additional_score`: điểm từ các thuộc tính mới được enrichment
- `alpha + beta = 1`

Ví dụ có thể chọn `alpha = 0.7` và `beta = 0.3` để đảm bảo form cơ bản vẫn chi phối phần lớn quyết định, còn nhu cầu thêm đóng vai trò tinh chỉnh.

### Bước 6. Cắt còn Top 5 và chuyển cho LLM giải thích
Sau bước re-ranking, hệ thống lấy `Top 5` cuối cùng và chuyển cho LLM để sinh lời giải thích.

LLM ở bước cuối chỉ nên:
- giải thích vì sao thứ hạng đã thay đổi sau khi xét thêm nhu cầu mới
- nêu rõ bất động sản nào phù hợp hơn với nhu cầu bổ sung
- tóm tắt điểm mạnh, điểm yếu của từng phương án

LLM không nên tự thêm tiêu chí mới hoặc tự thay đổi thứ hạng ngoài kết quả từ inference engine.

### Cấu trúc output gợi ý
Một response phù hợp cho bước giải thích có thể gồm cả điểm nền và điểm sau enrichment:

```python
bds_recommendation = [
    {
        "name": "Chung cu ABC",
        "base_score": 0.78,
        "additional_score": 0.90,
        "final_score": 0.82,
        "base_attributes": {
            "price": {
                "value": 3000,
                "unit": "million_vnd",
                "contribution_score": 0.27
            }
        },
        "dynamic_attributes": {
            "nearby_market_count_within_1km": {
                "value": 4,
                "unit": "place",
                "source": "map_api",
                "preference_type": "higher_better",
                "normalized_score": 0.90,
                "contribution_score": 0.18
            }
        }
    }
]
```

Điểm mạnh của cấu trúc này là hệ thống có thể chỉ ra rõ bất động sản được tăng hạng vì tiêu chí nào đến từ form và tiêu chí nào đến từ nhu cầu bổ sung.

### Pipeline đề xuất

`Form + Additional User Request -> LLM Requirement Parsing -> Rule-based Top 10 -> Tool-based Attribute Enrichment -> Post-filtering -> Re-scoring/Re-ranking -> Top 5 -> LLM Explanation`

Nếu viết ngắn gọn vào báo cáo, có thể kết luận: Solution 2 là một hướng hybrid, trong đó rule-based đảm bảo tính ổn định và minh bạch, còn LLM giúp hệ thống hiểu thêm các nhu cầu mới, mơ hồ hoặc chưa được mô hình hóa sẵn.