# Bản Thô Báo Cáo - Validation và Evaluation

## 1. Mục tiêu validation

Phần validation do `Ấn` phụ trách nhằm kiểm tra ba câu hỏi chính:

1. Hai solution có giữ đúng hard constraints không?
2. Ranking Top 5 có phản ánh đúng nhu cầu người dùng không?
3. Khi user nhập free-text, solution có xử lý phần nhu cầu đo được và gắn cờ phần chưa đo được một cách minh bạch không?

Vì bài toán tư vấn bất động sản không có nhãn đúng/sai tự nhiên như classification, nhóm dùng validation theo scenario. Mỗi scenario gồm input form, free-text, expected hard constraints, expected soft priorities và unsupported requirements.

## 2. Validation set hiện tại

File chính: `data/validation_cases_v1.json`.

Sau cập nhật ngày `2026-07-15`, bộ validation có `13` case:

| Nhóm case | Case | Mục tiêu |
|---|---|---|
| `X-only` | `V1_001` - `V1_005` | Kiểm tra ranking trên tiêu chí nền có sẵn trong form/dataset |
| `X + Y` | `V1_006`, `V1_007`, `V1_008`, `V1_010`, `V1_011`, `V1_012`, `V1_013` | Kiểm tra free-text có thêm tiêu chí đo được như chợ, cafe, gym, nhà thuốc, mầm non |
| `unsupported` | `V1_009` | Kiểm tra nhu cầu chủ quan như yên tĩnh, dân trí cao, phong thủy, hàng xóm thân thiện |

Các `user_need_text` đã được đổi sang tiếng Việt có dấu để tránh nhập nhằng. Ví dụ: nếu viết không dấu, `cho` có thể là `chợ`, `cho thuê`, hoặc `chỗ`. Sau khi thêm dấu, `V1_006` ghi rõ `chợ` và `trường mầm non`, giúp parser và rubric đánh giá đúng hơn.

## 3. Quy ước chấm điểm X + Y

Rubric chính nằm ở `docs/validation_rubric.md`.

Ký hiệu:

- `X`: tiêu chí nền có sẵn trong form hoặc dataset, ví dụ giá, diện tích, phòng ngủ, trường, công viên, bệnh viện, siêu thị, đường lớn.
- `Y`: tiêu chí sinh từ free-text và đo được bằng POI/tool, ví dụ chợ, quán cà phê, nhà thuốc, phòng gym, trường mầm non.
- `Y_unsupported`: tiêu chí chưa đo được hoặc quá chủ quan, ví dụ yên tĩnh, dân trí cao, hợp phong thủy, hàng xóm thân thiện.

Cause-effect khi chấm:

1. Nếu case chỉ có `X`, ground truth dùng ranking theo tiêu chí nền.
2. Nếu case có `Y` đo được, ground truth phải tính cả `Y`. Nếu không, solution xử lý đúng free-text sẽ bị phạt sai.
3. Nếu case có `Y_unsupported`, solution tốt phải đưa yêu cầu đó vào `unsupported_requirements`. Nếu solution tự cộng điểm cho tiêu chí không có dữ liệu, đó là lỗi nặng.
4. Nếu `Y` làm Top 1 thay đổi, explanation phải nói rõ thay đổi đó đến từ tiêu chí nào.

Ví dụ cụ thể:

- `V1_006`: user muốn `chợ trong vòng 1km` và `trường mầm non`. Ranking phải xét thêm market/kindergarten, không chỉ school/park/supermarket nền.
- `V1_007`: user muốn `nhà thuốc` và `phòng gym`. Ranking bỏ qua hai tiêu chí này là chưa phản ánh đủ free-text.
- `V1_009`: user muốn `yên tĩnh`, `dân trí cao`, `phong thủy`, `hàng xóm thân thiện`. Đây là nhóm chưa có dữ liệu đo trực tiếp, nên phải gắn cờ unsupported.

## 4. Compare sơ bộ hiện có

File compare sơ bộ: `outputs/solution_comparison_v1_preliminary.md`.

Bảng này chỉ dùng 10 case đang có output từ cả hai solution. Ba case mới `V1_011` - `V1_013` chưa có output nên chưa đưa vào kết luận cuối.

Kết quả sơ bộ:

| Chỉ số | Giá trị |
|---|---:|
| Số case đã compare | 10 |
| Case còn thiếu output | 3 (`V1_011`, `V1_012`, `V1_013`) |
| Same Top 1 | 8/10 |
| Average Top5 overlap | 4.00/5 |
| Avg latency Solution 2 | 15,559.8 ms |
| Avg latency Solution 1 | 239,221.0 ms |

Diễn giải:

- Hai solution hiện khá đồng nhất ở các case nền `X-only`: nhiều case cùng Top 1 và Top 5 trùng cao.
- `V1_008` và `V1_010` cần manual review vì Top 1 khác nhau.
- Latency của Solution 1 cao hơn rõ rệt vì pipeline gọi nhiều lượt LLM/tool hơn, còn Solution 2 chạy nhanh hơn trên nhiều case.

## 5. Case cần review kỹ

### V1_008 - Investor, nhiều chợ

- Solution 2 Top 1: `TB_035`
- Solution 1 Top 1: `GV_010`
- Top5 overlap: `4/5`

Cause-effect:

1. User muốn đầu tư, giá/m2 thấp, gần đường lớn, nhiều chợ.
2. `nhiều chợ` là `Y` đo được.
3. Solution 2 đưa `TB_035` lên Top 1 vì có `nearby_market_count_within_1000m = 3` và `additional_score = 1.0`.
4. Solution 1 vẫn chọn `GV_010`, nghiêng về tiêu chí nền hơn.
5. Vì vậy case này phải review theo rule `X + Y`, không được dùng ground truth `X-only`.

### V1_010 - Couple, cafe và đường lớn

- Solution 2 Top 1: `GV_010`
- Solution 1 Top 1: `GV_002`
- Top5 overlap: `4/5`

Cause-effect:

1. User muốn gần đường lớn, nhiều quán cà phê, nhưng cũng muốn yên tĩnh.
2. `quán cà phê` là `Y` đo được; `yên tĩnh` là unsupported.
3. Solution 2 chọn `GV_010` vì cafe count cao và vẫn cân bằng tiện ích nền.
4. Solution 1 chọn `GV_002` vì giá rẻ và gần đường lớn hơn.
5. Case này cần so explanation: solution nào giải thích rõ trade-off giữa cafe, đường lớn, yên tĩnh và diện tích tốt hơn.

## 6. Phần còn chờ thành viên khác

Phần độc lập của `Ấn` đã hoàn thành ở mức framework:

- Validation set đã mở rộng lên 13 case.
- Rubric đã chốt cách chấm `X-only`, `X + Y`, `unsupported`.
- Template compare đã cập nhật đúng Solution 1 vs Solution 2.
- Compare sơ bộ 10 case đã có sẵn.

Phần final còn chờ:

1. `Phú` chạy lại Solution 1 trên đủ 13 case.
2. `Quang` chạy lại Solution 2 trên đủ 13 case.
3. Sau khi có đủ output, `Ấn` cập nhật compare final và kết luận winner theo từng case.

## 7. Kết luận tạm thời

Ở trạng thái hiện tại, chưa nên kết luận solution nào thắng chung cuộc vì còn thiếu 3 case mới và 2 case cần manual review. Tuy nhiên, phần validation framework đã đủ để nhóm tiếp tục: mọi case đã có scope chấm rõ ràng, ground truth không còn bị lệch giữa `X-only` và `X + Y`, và các yêu cầu unsupported đã có cách xử lý minh bạch.
