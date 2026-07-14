# Chi tiết Solution 1

> Cập nhật `2026-07-14`:
> `Solution 1` hiện tại là hướng **pipeline tuần tự hai LLM có guardrail** của `Phú`.
> Hướng MCDA/TOPSIS trước đó đã bị thay thế để khớp với source đang có trong `src/solution1/`
> và output sơ bộ trong `outputs/solution1_results.json`.

## 1. Tóm tắt hướng tiếp cận

Solution 1 dùng LLM theo cách có kiểm soát, không để LLM tự trị tự do quyết định toàn bộ quy trình. Hệ thống gồm hai vai trò LLM:

- **LLM reasoner**: đọc form và nhu cầu tự nhiên, bắt buộc gọi công cụ lọc dữ liệu, có thể gọi thêm công cụ enrichment nếu người dùng yêu cầu tiện ích chưa có sẵn trong dataset, sau đó sinh danh sách ứng viên kèm điểm và lý do.
- **LLM explainer**: nhận Top 5 đã qua guardrail và viết giải thích trade-off bằng tiếng Việt tự nhiên. LLM này không có quyền gọi tool và không được thay đổi ranking.

Điểm quan trọng nhất là **Top 5 cuối cùng luôn phải thuộc tập bất động sản trong cơ sở dữ liệu**. LLM không được tự bịa thêm property ID hoặc tự đề xuất căn ngoài dataset.

## 2. Pipeline tổng quát

```text
form + free_text
-> hard constraints từ form
-> LLM reasoner gọi sql_filter
-> optional dynamic enrichment theo free_text
-> LLM reasoner sinh candidates + total_score
-> guardrail grounding bằng code
-> LLM explainer sinh giải thích
-> output contract chung
```

Trong đó:

1. **Hard filter** sinh từ form, ví dụ `budget_max_million` và `min_bedrooms`.
2. **sql_filter** lọc candidate trong database theo điều kiện cứng.
3. **Dynamic enrichment** chỉ chạy khi free-text yêu cầu tiện ích ngoài nhóm đã có sẵn.
4. **Guardrail** loại property ID không thuộc candidate set, loại trùng, sort theo điểm giảm dần, đánh lại rank và cắt Top 5.
5. **Explainer** viết giải thích dựa trên Top 5 đã khóa.

## 3. Tool và dữ liệu sử dụng

Solution 1 dùng database 100 bất động sản đã enrich làm nguồn dữ liệu chính. Các field nền gồm giá, diện tích, số phòng, quận/phường, tọa độ và các khoảng cách tiện ích đã có sẵn.

Các tool chính:

| Tool | Vai trò | Ghi chú kiểm soát |
|---|---|---|
| `sql_filter` | Lọc bất động sản theo điều kiện cứng | Điều kiện luôn được merge với hard constraints từ form |
| `fetch_nearby_custom` | Enrich tiện ích theo loại, ví dụ nhà thuốc, phòng gym, quán cà phê | Chỉ chạy trên candidate set, không mở rộng tập BĐS |
| `get_distance_to_place` | Tính khoảng cách đến một địa điểm cụ thể | Dùng khi free-text nhắc địa chỉ/tên riêng |

Các câu truy vấn SQL được kiểm soát bằng whitelist cột/toán tử và bind parameter, không nối chuỗi trực tiếp từ output LLM vào SQL.

## 4. Guardrail grounding

Guardrail là phần bắt buộc của Solution 1. Sau khi LLM reasoner trả về candidates, code kiểm tra:

- `property_id` phải nằm trong candidate set từ `sql_filter`.
- Không có `property_id` trùng.
- `top5` được sắp xếp giảm dần theo `total_score`.
- Rank được đánh lại liên tục từ 1.
- Nếu sau guardrail còn ít hơn 5 căn thì vẫn trả ít hơn 5, không backfill bằng căn ngoài candidate set.

Cơ chế này bảo vệ tính công bằng khi so sánh giữa các solution: Solution 1 có thể dùng LLM để reasoning, nhưng không được vượt khỏi dữ liệu đã kiểm soát.

## 5. Enrichment động và vấn đề X + Y

Bộ dữ liệu enriched ban đầu có nhóm tiện ích nền `X`, ví dụ trường học, công viên, bệnh viện, siêu thị và trục đường lớn. Khi free-text nhắc thêm tiện ích ngoài nhóm này, Solution 1 có thể enrich thêm nhóm thuộc tính `Y`, ví dụ:

- nhà thuốc trong bán kính 1 km;
- phòng gym gần nhà;
- quán cà phê;
- chợ;
- khoảng cách đến nơi làm việc cụ thể.

Vì vậy, validation cần ghi rõ từng scenario được đánh giá trên:

- chỉ nhóm tiện ích nền `X`; hay
- nhóm `X + Y`, tức có tính đến tiện ích động mà Solution 1 đã enrich.

Nếu ground truth chỉ xét `X` trong khi Solution 1 dùng thêm `Y`, kết quả đánh giá có thể bị lệch, vì một lựa chọn được chấm cao nhờ tiện ích mới nhưng nhãn relevance không phản ánh tiêu chí đó.

## 6. Output hiện có

Phú đã chạy thử 10 validation case đầu tiên. Trạng thái sơ bộ:

- 10/10 case chạy `ok`.
- Mỗi case trả về đủ Top 5.
- Top 5 đã qua guardrail và thuộc dataset.
- Một số case chỉ gọi `sql_filter`; một số case gọi thêm dynamic enrichment.
- Latency còn cao, trung bình khoảng 239 giây/case trong lần chạy sơ bộ.

Output tham chiếu:

- `outputs/solution1_results.json`
- `outputs/explanations/V1_001.md` đến `V1_010.md`

Các explanation cần được review thủ công vì có thể còn lỗi ngôn ngữ, quá dài hoặc suy diễn ngoài dữ liệu.

## 7. Metric đánh giá đề xuất

| Nhóm metric | Metric |
|---|---|
| Độ phù hợp | CSR, NDCG@5, MAP@5, human relevance |
| Grounding | Grounding Pass Rate, duplicate rate, hard-constraint pass |
| Tool-use | Tool-call correctness, dynamic enrichment usefulness |
| Giải thích | Explanation faithfulness, độ ngắn gọn, lỗi ngôn ngữ |
| Vận hành | Latency, số lượt gọi LLM, số lượt gọi tool, tỷ lệ case dùng enrichment động |

Definition of done cho Solution 1:

- Output đúng contract chung.
- Top 5 không bịa property ngoài dataset.
- LLM reasoner gọi đúng tool trong các case cần enrichment động.
- Explanation bám dữ liệu, không thêm thông tin pháp lý/an ninh/đường sá nếu dataset không có.
- Validation ghi rõ case nào dùng `X` và case nào dùng `X + Y`.

## 8. Tóm tắt

```text
Solution 1 = Two-LLM sequential pipeline + SQL/tool-use + grounding guardrail + explanation
Solution 2 = Hybrid form + LLM parser + map enrichment + deterministic re-ranking
```

Hai solution khác nhau ở mức độ kiểm soát:

- Solution 1 cho LLM nhiều quyền reasoning hơn, nhưng khóa biên dữ liệu bằng guardrail.
- Solution 2 để code/inference engine kiểm soát ranking rõ hơn, LLM chủ yếu parse nhu cầu và giải thích.
