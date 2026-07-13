# Timeline Cập Nhật Cho Mốc Báo Cáo 24/07/2026

Ngày cập nhật: `2026-07-11`

Mục tiêu:
- `24/07/2026`: nhóm báo cáo cuối kỳ với thầy bằng slide và nộp slide.
- Báo cáo viết cần có bản draft hoàn chỉnh **trước ngày báo cáo ít nhất 1 tuần**.
- Sau buổi báo cáo, report vẫn có thể chỉnh nếu thầy yêu cầu.

Mục tiêu vận hành mới:
- **Hoàn thành phần việc chính trước `20/07/2026`**.
- **Mỗi thành viên phải bàn giao slide phần mình trước `20/07/2026`**.
- Giai đoạn `21/07 - 24/07` chỉ dành cho:
  - ôn tập
  - luyện báo cáo
  - chạy demo thử
  - rà slide / report / câu hỏi phản biện

## 1. Điều chỉnh so với plan cũ

### Nhận định quan trọng

`Ấn` **có thể làm độc lập một phần lớn** của validation, không cần chờ hoàn toàn `Phú` và `Quang` ngay từ đầu.

Cụ thể, `Ấn` có thể tự làm trước:
- chốt `output contract`
- tạo `validation set` bản 1
- chốt `rubric`
- dựng `template compare`
- chuẩn bị protocol đánh giá
- chuẩn bị phần slide/report khung cho validation

Phần của `Ấn` **phụ thuộc vào `Phú` / `Quang`** chỉ bắt đầu từ lúc:
- nhận output chạy thật của `Solution 2`
- nhận output chạy thật của `Solution 1`
- tổng hợp compare và viết kết luận cuối

Vì vậy, timeline mới nên tách:
1. phần validation độc lập
2. phần evaluation phụ thuộc output thật

## 2. Trạng thái hiện tại theo đầu ra trong repo

| Thành viên | Phụ trách | Đã hoàn thành | Chưa hoàn thành | Phụ thuộc | Trạng thái |
| --- | --- | --- | --- | --- | --- |
| `Quang` | `Solution 2` | Đã có code trong `src/solution2/`, đã có `outputs/solution2_results.json`, output hiện khá gần contract chung | Cần chốt output final để evaluate chính thức, cần chốt slide/report | Cần confirm output cuối với `Ấn` | `tiến độ tốt / gần hoàn thành kỹ thuật` |
| `Phú` | `Solution 1` | Đã chốt hướng MCDA/TOPSIS là phần phụ trách chính | Chưa thấy output final tương ứng trong repo, cần chốt pipeline, map đúng contract chung, chuẩn bị slide/report | Cần thống nhất contract với `Ấn` và scope demo với cả nhóm | `đang làm / chưa chốt` |
| `Tiến` | Data / Enrich / Dataset | Đã có dataset 100 căn, pipeline API `Overpass` và `Geoapify`, Geoapify đã chạy đủ 100 mẫu, đã có schema doc, curl mẫu, provider comparison, README cập nhật | Cần chốt file dataset final dùng cho demo/report, hỗ trợ ghép slide chung | Phụ thuộc scope demo cuối của cả nhóm | `gần hoàn thành` |
| `Ấn` | Validation / Evaluation | Đã có `output contract`, `validation set` bản 1, `rubric`, `compare template` | Cần nhận output final từ `Solution 2` và `Solution 1`, chạy evaluation cuối, viết kết luận compare, làm slide validation final | Phụ thuộc output cuối từ `Phú` và `Quang` | `phần độc lập đã xong phần lớn` |

Ghi chú:
- Repo hiện đang bám 2 hướng final chính là `Solution 1` và `Solution 2`.
- Timeline này chỉ theo dõi phần việc hiện tại, không nhắc lại các hướng cũ.

## 3. Kết luận phân công hiện tại

- `Ấn` có thể và nên tiếp tục làm độc lập phần validation framework ngay từ bây giờ.
- Nút thắt hiện tại không phải validation framework, mà là:
  - `Phú` chưa chốt `Solution 1` và output đúng contract
  - `Quang` cần bàn giao output final của `Solution 2` để compare chính thức
  - cả nhóm cần chốt hướng demo chính và nội dung slide/report

## 4. Timeline cập nhật từ nay đến 24/07/2026

| Giai đoạn | Mục tiêu chính | `Phú` | `Quang` | `Tiến` | `Ấn` |
| --- | --- | --- | --- | --- | --- |
| `Tuần 1: 11/07 - 13/07` | Khóa scope, khóa dữ liệu, khóa contract, chốt phần việc còn thiếu | Chốt hướng và pipeline cuối của `Solution 1`, map output sang contract chung, chạy thử vài case validation. Trạng thái hiện tại: `chưa xong` | Chốt output gần-final của `Solution 2`, rà lại các case free-text và unsupported requirements. Trạng thái hiện tại: `gần xong phần kỹ thuật` | Khóa dataset/demo source chính, ưu tiên `Geoapify` làm provider demo và `Overpass` làm baseline so sánh, cập nhật note file cũ/outdated. Trạng thái hiện tại: `đã làm gần xong` | Chuẩn bị / mở rộng validation set bằng khảo sát người dùng hoặc LLM sinh scenario theo rule, đồng thời chốt rubric, khung compare và khung evaluation/report. Trạng thái hiện tại: `phần độc lập đã xong phần lớn` |
| `Tuần 1: 14/07 - 17/07` | Hai solution phải ra output đúng contract; mỗi thành viên phải chốt report draft và slide phần mình | Bàn giao output `Solution 1`, fix theo feedback, chốt report draft + slide `Solution 1` | Bàn giao output `Solution 2`, fix theo feedback, chốt report draft + slide `Solution 2` | Chốt file dữ liệu chính cho demo, chốt report dataset + slide dataset, ghép draft slide chung | Nhận output, chạy compare/evaluation chính thức, chốt report validation + slide validation |
| `Tuần 2: 18/07 - 20/07` | Hoàn tất toàn bộ bài, ghép bản final, xem như xong việc chính trước ngày báo cáo | Rà logic trình bày, chốt nội dung nói, chốt demo case của `Solution 1` | Rà logic trình bày, chốt demo case của `Solution 2`, chuẩn bị backup nếu demo lỗi | Chốt final slide deck, flow trình bày, dữ liệu demo | Chốt final report draft, soát consistency giữa metric, compare, contract và phần trình bày |
| `Tuần 2: 21/07 - 24/07` | Chỉ ôn tập, rehearsal, chuẩn bị phản biện và báo cáo chính thức | Rehearsal full talk, chuẩn bị câu trả lời ngắn/dài | Rehearsal demo, chuẩn bị phương án backup | Rà visual cuối, thứ tự trình bày, nhịp chuyển slide | Rehearsal phần validation, chốt note câu hỏi phản biện và kết luận compare |

## 5. Gợi ý cách dùng bảng này

- Nếu nhóm cần nhìn nhanh để họp, dạng bảng rõ hơn dạng bullet.
- Nếu cần viết dài cho report, có thể giữ bảng này ở đầu rồi thêm phần diễn giải ngắn bên dưới.
- Với buổi họp nhóm, chỉ cần tô màu 3 trạng thái: `đã xong`, `đang làm`, `bị chặn` là nhìn rất nhanh.

## 6. Ghi chú trạng thái hiện tại

- Giai đoạn `11/07 - 13/07` hiện được xem là **đã hòm hòm / gần hoàn tất**.
- Giai đoạn `11/07 - 13/07` hiện được xem là **đã hòm hòm / gần hoàn tất**.
- Bộ `100` BĐS cho demo về cơ bản đã được khóa.
- Hướng final cũng đã rõ:
  - `Solution 1`: MCDA/TOPSIS của `Phú`
  - `Solution 2`: hybrid của `Quang`
- Phần còn cần chốt thêm trong giai đoạn này chủ yếu là:
  - file dataset/enriched file nào sẽ được gọi là file chính cho demo
  - bộ key tiện ích xung quanh nào thực sự đi vào scoring/demo/report
  - output contract cuối cùng để `Ấn` chạy compare chính thức
  - cách tạo validation set cuối: survey người dùng, LLM sinh theo rule, hoặc kết hợp cả hai

## 7. Việc cần xong theo từng người

| Thành viên | Phải xong trước | Đầu việc cần chốt |
| --- | --- | --- |
| `Phú` | `15/07` | Output `Solution 1` đúng contract |
| `Phú` | `17/07` | Report draft `Solution 1`, **slide `Solution 1` đã bàn giao** |
| `Phú` | `20/07` | Chốt nội dung trình bày và demo case của `Solution 1` |
| `Quang` | `15/07` | Output `Solution 2` đúng contract |
| `Quang` | `17/07` | Report draft `Solution 2`, **slide `Solution 2` đã bàn giao** |
| `Quang` | `20/07` | Chốt nội dung trình bày và demo case của `Solution 2` |
| `Tiến` | `14/07` | Khóa dataset/demo source chính |
| `Tiến` | `17/07` | Report dataset, **slide dataset đã bàn giao**, ghép draft slide chung |
| `Tiến` | `20/07` | Chốt final slide deck và flow demo dữ liệu |
| `Ấn` | `14/07` | Validation framework độc lập hoàn chỉnh |
| `Ấn` | `17/07` | Bảng compare kết quả thật, report validation/evaluation, **slide validation đã bàn giao** |
| `Ấn` | `20/07` | Chốt final report draft và consistency giữa compare, metric, contract |

## 8. Khuyến nghị thực tế cho nhóm

1. Chốt ngay rằng `Ấn` được phép tiếp tục làm validation độc lập, không cần đợi full output mới bắt đầu.
2. `Phú` là điểm cần đẩy mạnh nhất lúc này vì `Solution 1` hiện chưa thấy output final rõ ràng trong repo.
3. `Quang` nên khóa output final của `Solution 2` rất sớm để `Ấn` có mốc compare trước `16/07`.
4. `Tiến` nên chốt rõ: demo chính dùng `Geoapify`, còn `Overpass` là compare/baseline.
5. Mốc nhóm cần tự xem là “xong bài” nên là **`20/07/2026`**, không phải sát `24/07`.
6. Trước `17/07`, mỗi thành viên phải bàn giao **slide phần mình**, không chỉ bàn giao code hoặc report.
7. Từ `21/07` trở đi, cả nhóm không mở thêm scope mới; chỉ rehearsal, ổn định demo, và chuẩn bị câu hỏi phản biện.
