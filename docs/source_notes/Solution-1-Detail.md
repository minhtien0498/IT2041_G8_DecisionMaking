# Chi tiết Solution 1

## Form + Free-Text → LLM Agent (Tool Use) → Iterative Reasoning → Top 5 + Explanation

Ý tưởng cốt lõi của Solution 1 là **LLM hoạt động như một agent được trang bị bộ tool cụ thể**, tự lên kế hoạch, gọi tool và đánh giá kết quả theo vòng lặp cho đến khi tìm được đủ ứng viên đa dạng. Thay vì chạy theo một pipeline cố định, LLM **tự quyết định chiến lược tìm kiếm** dựa trên input và system prompt — linh hoạt điều chỉnh theo từng truy vấn. Theo cách này, LLM không chỉ là lớp giải thích mà là **bộ não chủ đạo** của toàn bộ quy trình.

### Bước 1. Người dùng nhập Form + Nhu cầu thêm
Input gồm 2 phần:
1. **Form cố định**: các tiêu chí cơ bản có thể định lượng (ngân sách, số phòng, khoảng cách tối đa đến trường học / công viên / trục giao thông). Phần này cung cấp ngữ cảnh rõ ràng để LLM không cần đoán mò các thông tin cơ bản.
2. **Nhu cầu thêm** *(tùy chọn)*: mô tả tự do bằng ngôn ngữ tự nhiên cho các mong muốn bổ sung mà form chưa bao phủ:
   - "Muốn nơi ở yên tĩnh nhưng vẫn tiện lợi"
   - "Gần nhiều tiện ích ăn uống, sống động"
   - "Ưu tiên khu dân cư an toàn, xanh mát"

LLM sẽ **gộp form và nhu cầu thêm thành một biểu diễn ngữ nghĩa thống nhất** để làm đầu vào cho agent. Phần nhu cầu thêm thường **có tính mơ hồ cao**: "yên tĩnh" có nhiều ý nghĩa, "tiện lợi" không rõ ngưỡng — agent sẽ tự khám phá các diễn giải này bằng cách gọi tool từ nhiều góc độ.

### Bước 2. Khai báo tools và thiết kế System Prompt

Trước khi agent bắt đầu, hệ thống cần khai báo **bộ tool** mà LLM được phép sử dụng và thiết kế **system prompt** để định hướng cách suy luận.

**Bộ tool được khai báo:**

| Tool | Mục đích | Input | Output |
|---|---|---|---|
| `sql_filter(conditions)` | Lọc BĐS theo điều kiện cứng từ relational DB | dict điều kiện | Danh sách BĐS |
| `vector_search(query, top_k)` | Tìm kiếm ngữ nghĩa trên Vector DB | câu truy vấn tự nhiên | Danh sách BĐS |
| `fetch_nearby(lat, lon, amenity, radius_m)` | Lấy tiện ích xung quanh qua Map API | tọa độ + loại tiện ích | Danh sách POI + khoảng cách |
| `get_distance(address_a, address_b)` | Tính khoảng cách đến một địa điểm | 2 địa chỉ hoặc tọa độ | Khoảng cách (m) |

**System Prompt định hướng:**

System prompt được thiết kế để hướng dẫn LLM:
- **Mục tiêu**: tìm Top 5 BĐS đa dạng, bao phủ nhiều góc nhìn khác nhau.
- **Chiến lược**: khai thác hard constraint từ form trước, sau đó khám phá các diễn giải của nhu cầu thêm.
- **Diversity**: đảm bảo Top 5 không đến từ cùng một nhóm.
- **Stop condition**: dừng khi đã có đủ ứng viên đa dạng hoặc đạt giới hạn tool calls.
- **Few-shot examples**: ví dụ về chain-of-thought tốt được nhúng vào system prompt để tăng chất lượng suy luận và tính nhất quán.

### Bước 3. Vòng lặp suy luận — hành động — quan sát (ReAct Loop)

LLM hoạt động theo vòng lặp **Reason → Act → Observe** cho đến khi đủ điều kiện dừng:

1. **Reason**: LLM đọc input, đánh giá trạng thái hiện tại và quyết định tool nào cần gọi tiếp theo.
2. **Act**: LLM gọi tool với tham số phù hợp.
3. **Observe**: LLM nhận kết quả, đánh giá độ đa dạng và quyết định có cần lặp tiếp không.

Ví dụ một phiên chạy:

```
[Input]
Form: ngân sách 5 tỷ / 3 phòng ngủ / gần trường < 500m
Nhu cầu thêm: "Muốn yên tĩnh nhưng vẫn tiện lợi"

[Reason] Hard constraints rõ ràng: 3 phòng, ≤ 5B, gần trường.
         "Yên tĩnh" và "tiện lợi" có thể xung đột — cần khám phá cả hai góc.
         → Dùng sql_filter trước để lọc hard constraints.

[Act]     sql_filter({"bedrooms": 3, "max_price": 5000000000, "max_dist_school": 500})
[Observe] 12 BĐS hợp lệ. Tiếp tục khám phá nhu cầu mơ hồ.

[Reason] Tìm theo góc "yên tĩnh, xanh mát".
[Act]     vector_search("quiet residential area, green, peaceful", top_k=8)
[Observe] 6 BĐS overlap với SQL. Nhóm này thiên về yên tĩnh.

[Reason] Cần kiểm tra góc "tiện lợi, nhiều tiện ích" để có diversity.
[Act]     vector_search("convenient neighborhood, amenities nearby, vibrant", top_k=8)
[Observe] 5 BĐS khác. Nhóm này thiên về sôi động.

[Reason] Có 2 nhóm rõ. Kiểm tra tiện ích thực tế cho ứng viên tiềm năng.
[Act]     fetch_nearby(lat=10.845, lon=106.624, amenity="park", radius_m=1000)
[Observe] BĐS A có 2 công viên trong 1km — phù hợp góc "yên tĩnh xanh mát".

[Reason] Đã đủ đa dạng để chọn Top 5. → STOP
```

### Bước 4. Điều kiện dừng và chọn Top 5

Agent dừng khi một trong các điều kiện sau được thỏa mãn:
- Đã có ứng viên đa dạng từ ít nhất 2 góc nhìn khác nhau.
- Đã đạt giới hạn tool calls tối đa (safety limit, ví dụ 10 calls).
- LLM tự đánh giá không cần thêm thông tin.

Sau khi dừng, LLM chọn Top 5 đảm bảo:
- Ít nhất 2 góc nhìn được đại diện.
- Ứng viên đầu tiên phù hợp nhất tổng thể.
- Các ứng viên còn lại thể hiện tradeoff rõ ràng.

### Bước 5. LLM sinh lời giải thích

Dựa trên reasoning trace và Top 5 đã chọn, LLM sinh lời giải thích:
- Tại sao mỗi BĐS được chọn.
- Tradeoff giữa các lựa chọn (yên tĩnh vs sôi động, giá vs tiện ích...).
- Gợi ý ưu tiên dựa trên tín hiệu từ nhu cầu thêm.

Có thể dùng cùng LLM call hoặc một call riêng để đồng bộ format với Solution 2.

### Cấu trúc output gợi ý

```python
bds_recommendation = [
    {
        "rank": 1,
        "name": "Nhà phố ABC",
        "overall_score": 0.86,
        "perspective": "balanced",
        "key_attributes": {
            "price": "4.8 tỷ",
            "bedrooms": 3,
            "dist_school": "450m",
            "nearby_parks": 2
        },
        "why_recommended": "Cân bằng giữa yên tĩnh và tiện lợi. Gần trường, có công viên, tiện ích đủ dùng.",
        "tradeoff": "Không phải yên tĩnh nhất nhưng không thiếu tiện ích"
    }
]
```

### Pipeline đề xuất

`Form + Free-Text → LLM Agent (System Prompt + Tools) → [Reason → Act → Observe]* → Top 5 → LLM Explanation`

### Ưu điểm của Solution 1

1. **Linh hoạt, không pipeline cứng**: Agent tự quyết định chiến lược tìm kiếm, thích nghi với từng truy vấn thay vì chạy theo bước cố định. Chất lượng suy luận được tinh chỉnh qua **system prompt** và **few-shot examples** mà không cần thay đổi code.
2. **Tổng hợp đa nguồn**: Kết hợp SQL (hard filter), Vector DB (semantic), Map API (spatial) trong cùng một phiên suy luận.
3. **Dễ mở rộng**: Thêm tool mới không cần thay đổi core logic — chỉ cần khai báo và cập nhật system prompt.
4. **Transparency**: Reasoning trace là chuỗi giải thích tự nhiên, dễ kiểm tra và debug.
5. **Diversity**: Top 5 được đảm bảo từ nhiều góc nhìn khác nhau.
6. **Modern AI**: Theo hướng LLM Agent / ReAct — xu hướng chính hiện tại của AI ứng dụng.
