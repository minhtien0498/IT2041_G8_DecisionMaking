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

## 4. Compare hiện tại: Solution 1 Mapbox vs Solution 2

File compare mới: `outputs/solution_comparison_mapbox_v1.md`.

Sau khi pull main ngày `2026-07-22`, repo đã có:

- Solution 1 Mapbox: 10 case `V1_001` - `V1_010`.
- Solution 2: 13 case `V1_001` - `V1_013`.

Bảng này compare 10 case chung vì Solution 1 chưa có `V1_011` - `V1_013`.

| Chỉ số | Giá trị |
|---|---:|
| Số case đã compare | 10 |
| Solution 1 Mapbox coverage | 10/10 |
| Solution 2 coverage | 13/13 |
| Same Top 1 | 4/10 |
| Average Top5 overlap | 2.50/5 |
| Avg latency Solution 1 Mapbox | 481,044.9 ms |
| Avg latency Solution 2 | 2.2 ms |

Cause-effect:

1. Mapbox là provider final được ghi trong docs.
2. Solution 1 Mapbox giờ có output thật, nên compare chính nên dùng bản Mapbox thay vì file Solution 1 cũ.
3. Solution 2 đã chạy đủ 13 case, nhưng Solution 1 mới có 10 case.
4. Vì vậy kết luận final vẫn phải chờ Solution 1 chạy thêm `V1_011` - `V1_013`.

## 5. Provider Sensitivity của Solution 1

File compare provider mới: `outputs/solution1_provider_comparison_mapbox_geoapify_overpass.md`.

Solution 1 hiện đã có kết quả riêng cho cả 3 provider trên 10 case `V1_001` - `V1_010`.

| Chỉ số | Giá trị |
|---|---:|
| Mapbox coverage | 10/10 |
| Geoapify coverage | 10/10 |
| Overpass coverage | 10/10 |
| Same Top 1 cả 3 provider | 2/10 |
| Same Top 1 Mapbox vs Geoapify | 4/10 |
| Same Top 1 Mapbox vs Overpass | 2/10 |
| Same Top 1 Geoapify vs Overpass | 4/10 |
| Avg Top5 overlap Mapbox vs Geoapify | 2.30/5 |
| Avg Top5 overlap Mapbox vs Overpass | 2.00/5 |
| Avg Top5 overlap Geoapify vs Overpass | 3.20/5 |
| Avg latency Mapbox | 481,044.9 ms |
| Avg latency Geoapify | 317,397.1 ms |
| Avg latency Overpass | 529,236.6 ms |

Cause-effect:

1. `SOLUTION1_ENRICHMENT_PROVIDER` chọn provider cho cả file dataset nạp vào DB và tool map động.
2. Provider khác nhau trả về POI distance/count khác nhau.
3. POI khác nhau làm Top 1 và Top 5 thay đổi.
4. Vì vậy kết quả Solution 1 phải ghi rõ provider, không nên gộp Mapbox, Geoapify và Overpass thành một kết quả chung.

Case lệch mạnh cần review thêm:

- `V1_004`: Mapbox Top 1 `GV_010`, Geoapify Top 1 `TB_015`, Overpass Top 1 `GV_003`.
- `V1_006`: Mapbox/Geoapify Top 1 `GV_008`, Overpass Top 1 `GV_018`, Mapbox-Overpass overlap `0/5`.
- `V1_007`: Mapbox Top 1 `GV_003`, Geoapify Top 1 `GV_009`, Overpass Top 1 `GV_002`.

Hiện vẫn thiếu:

- Output Solution 1 cho `V1_011` - `V1_013`.
- Compare final 13 case giữa Solution 1 Mapbox và Solution 2.

## 6. Case cần review kỹ

### V1_008 - Investor, nhiều chợ

- Solution 2 Top 1: `TB_035`
- Solution 1 Top 1: `GV_010`
- Top5 overlap: `4/5`

Cause-effect:

1. User muốn đầu tư, giá/m2 thấp, gần đường lớn, nhiều chợ.
2. `nhiều chợ` là `Y` đo được.
3. Solution 2 đưa `TB_035` lên Top 1 vì có `nearby_market_count_within_1000m = 3` và `additional_score = 1.0`.
4. Solution 1 Mapbox chọn `GV_037`, lệch khỏi Solution 2 và cần kiểm tra lại explanation theo tiêu chí market/price_per_m2.
5. Vì vậy case này phải review theo rule `X + Y`, không được dùng ground truth `X-only`.

### V1_010 - Couple, cafe và đường lớn

- Solution 2 Top 1: `GV_010`
- Solution 1 Mapbox Top 1: `GV_002`
- Top5 overlap: `4/5`

Cause-effect:

1. User muốn gần đường lớn, nhiều quán cà phê, nhưng cũng muốn yên tĩnh.
2. `quán cà phê` là `Y` đo được; `yên tĩnh` là unsupported.
3. Solution 2 chọn `GV_010` vì cafe count cao và vẫn cân bằng tiện ích nền.
4. Solution 1 Mapbox chọn `GV_002` vì giá rẻ và gần đường lớn hơn.
5. Case này cần so explanation: solution nào giải thích rõ trade-off giữa cafe, đường lớn, yên tĩnh và diện tích tốt hơn.

## 7. Phần còn chờ thành viên khác

Phần độc lập của `Ấn` đã hoàn thành ở mức framework:

- Validation set đã mở rộng lên 13 case.
- Rubric đã chốt cách chấm `X-only`, `X + Y`, `unsupported`.
- Template compare đã cập nhật đúng Solution 1 vs Solution 2.
- Compare hiện tại S1 Mapbox vs S2 và provider sensitivity đã có sẵn.

Phần final còn chờ:

1. `Phú` đã push Solution 1 cho Mapbox, Geoapify và Overpass trên 10 case; còn cần `V1_011` - `V1_013`.
2. `Quang` đã có Solution 2 đủ 13 case trong `outputs/solution2_results.json`.
3. Sau khi có đủ output, `Ấn` cập nhật compare final và kết luận winner theo từng case.

## 8. Kết luận tạm thời

Ở trạng thái hiện tại, chưa nên kết luận solution nào thắng chung cuộc vì còn thiếu 3 case mới và 2 case cần manual review. Tuy nhiên, phần validation framework đã đủ để nhóm tiếp tục: mọi case đã có scope chấm rõ ràng, ground truth không còn bị lệch giữa `X-only` và `X + Y`, và các yêu cầu unsupported đã có cách xử lý minh bạch.
