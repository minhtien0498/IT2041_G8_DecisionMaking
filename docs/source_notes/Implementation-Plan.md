# Kế hoạch triển khai - Kiểm soát tiến độ theo tuần

## 1. Mục tiêu
Triển khai song song Solution 1 và Solution 2 với 4 thành viên chia thành 2 nhóm độc lập, cùng sử dụng tập dataset chung đã có sẵn và xây dựng một validation set chung để đảm bảo so sánh công bằng, theo dõi tiến độ qua đầu ra và meeting cuối tuần.

## 2. Phân nhóm
- member-1: phụ trách thiết kế/triển khai Solution 1.
- member-2: phụ trách thiết kế/triển khai Solution 2.
- member-3: phụ trách rà soát dataset chung đã có, kiểm tra schema và chất lượng dữ liệu để hai solution cùng dùng ổn định.
- member-4: phụ trách xây dựng validation set và tiêu chí đánh giá dùng chung.

Phần validation là phần dùng chung, nên cần phân công chéo thay vì để mỗi nhóm tự làm riêng:
- member-1: tập trung vào pipeline và output của Solution 1.
- member-2: tập trung vào pipeline và output của Solution 2.
- member-3: đảm bảo dataset chung đủ sạch, đủ cột và thống nhất schema.
- member-4: đảm bảo validation set và output contract đủ rõ để hai solution chạy cùng chuẩn.

Hai thành viên phụ trách solution vẫn phải phối hợp với hai thành viên phụ trách dữ liệu/validation để đảm bảo cả hai solution chạy trên cùng một nguồn dữ liệu và cùng một chuẩn đánh giá.

## 3. Cách phân công chi tiết

### 3.1. Member-3 - Rà soát dataset chung

Nhiệm vụ chính:
- Kiểm tra dataset chung hiện có có đủ cột bắt buộc cho cả hai solution hay chưa.
- Chuẩn hóa tên cột, kiểu dữ liệu và khóa định danh của từng BĐS.
- Ghi nhận các dòng lỗi hoặc thiếu dữ liệu quan trọng để hai solution biết cách xử lý thống nhất.

Checklist tối thiểu:
- Mỗi BĐS phải có `property_id` duy nhất.
- Các cột quan trọng như `price`, `area`, `bedrooms`, `latitude`, `longitude`, `address` phải có quy ước thống nhất.
- Nếu có cột POI/enrichment thì phải ghi rõ cột nào đã có, cột nào chưa có.
- Nếu có giá trị thiếu, phải có file note hoặc bảng note ghi cách xử lý: bỏ dòng, điền null, hay giữ nguyên.

Đầu ra cần bàn giao trước:
- Một schema dataset chung đã chốt.
- Một danh sách các cột bắt buộc cho pipeline.
- Một ghi chú ngắn về các vấn đề dữ liệu mà hai solution phải lưu ý.

### 3.2. Member-4 - Dựng validation set dùng chung

Nhiệm vụ chính:
- Tạo validation set để cả Solution 1 và Solution 2 cùng chạy.
- Chốt format input/output đánh giá trước để member-1 và member-2 dựng pipeline theo cùng chuẩn.
- Tổng hợp kết quả chạy của hai solution để so sánh công bằng.

Cách dựng validation set:
1. Dùng dataset chung đã được member-3 rà soát làm nguồn BĐS duy nhất.
2. Tạo các `user scenario` đại diện cho nhiều nhóm nhu cầu:
   - nhu cầu rõ ràng
   - nhu cầu có free-text mơ hồ
   - nhu cầu có xung đột/tradeoff
   - nhu cầu có yêu cầu unsupported
3. Với mỗi scenario, điền đủ:
   - form input
   - free-text input
   - hard constraints kỳ vọng
   - soft priorities kỳ vọng
   - ghi chú review nếu case khó hoặc có ambiguity
4. Review chéo mỗi case ít nhất 1 lần để tránh case quá chủ quan.
5. Chốt một file validation set dùng chung trước khi member-1 và member-2 chạy pipeline.

Số lượng case tối thiểu nên có:
- 10 case rõ ràng
- 10 case có free-text mơ hồ
- 5 case mâu thuẫn/tradeoff mạnh
- 5 case unsupported hoặc đo lường khó

Member-4 không chỉ làm template. Member-4 cần bàn giao ít nhất một bản validation set có thể chạy được ngay, kể cả bản đầu tiên còn nhỏ.

### 3.3. Output contract mà member-4 phải đưa trước

Đây là phần phải chốt sớm nhất để member-1 và member-2 dựng pipeline đúng chuẩn.

#### A. Schema của một validation case

Mỗi case trong validation set nên có cấu trúc thống nhất như sau:

```json
{
  "case_id": "VAL_001",
  "persona": "family_with_children",
  "input": {
    "budget_max_billion": 6.0,
    "min_bedrooms": 3,
    "max_distance_school_m": 500,
    "max_distance_park_m": 1000,
    "max_distance_main_road_m": 800,
    "user_need_text": "Gia dinh co 2 con nho, uu tien gan truong va cong vien, khu vuc yen tinh."
  },
  "expected": {
    "hard_constraints": [
      "price <= 6.0 billion",
      "bedrooms >= 3"
    ],
    "soft_priorities": [
      "near school",
      "near park",
      "quiet area"
    ],
    "unsupported_requirements": []
  },
  "case_group": "ambiguous_free_text",
  "review_note": "Can uu tien giai thich tradeoff giua yen tinh va tien ich."
}
```

#### B. Schema output chuẩn mà mỗi solution phải trả ra

Member-1 và member-2 cần trả kết quả theo cùng một format để member-4 ghép vào bước evaluation:

```json
{
  "case_id": "VAL_001",
  "solution_id": "solution_1",
  "status": "ok",
  "top5": [
    {
      "rank": 1,
      "property_id": "GV_008",
      "total_score": 0.87,
      "hard_constraint_pass": true,
      "reason_tags": ["near_school", "near_park", "quiet_area"]
    }
  ],
  "explanation_summary": "Top 1 can bang giua gan truong, gan cong vien va muc gia phu hop.",
  "unsupported_requirements": [],
  "latency_ms": 1820
}
```

Các trường tối thiểu bắt buộc:
- `case_id`
- `solution_id`
- `status`
- `top5`
- `top5[].rank`
- `top5[].property_id`
- `top5[].total_score`
- `top5[].hard_constraint_pass`

Nếu solution có thêm dữ liệu riêng như `base_score`, `additional_score`, `tool_trace`, `cluster_label` thì được phép thêm, nhưng không được thiếu các trường tối thiểu phía trên.

#### C. Bảng kết quả tổng hợp do member-4 dựng

Sau khi nhận output từ hai solution, member-4 nên tổng hợp thành một file so sánh như sau:

```json
{
  "case_id": "VAL_001",
  "solution_1_top5": ["GV_008", "GV_035", "GV_029", "GV_031", "GV_007"],
  "solution_2_top5": ["GV_035", "GV_008", "GV_029", "GV_012", "GV_031"],
  "constraint_satisfaction_solution_1": 1.0,
  "constraint_satisfaction_solution_2": 1.0,
  "review_comment": "Solution 1 da dang hon; Solution 2 de giai thich hon."
}
```

### 3.4. Member-1 - Dựng Solution 1 theo contract chung

Member-1 cần chốt sớm:
- Input parser nhận đúng schema của validation case.
- Pipeline trả ra đúng schema output chuẩn.
- Nếu Solution 1 có thêm trace của agent/tool use thì để ở field mở rộng, không thay schema chung.

Cách dựng:
- Bước 1: nhận `input` từ validation case.
- Bước 2: chạy pipeline Solution 1.
- Bước 3: map kết quả nội bộ sang output contract chung.
- Bước 4: kiểm tra đủ 5 dòng output hay ghi rõ vì sao không đủ.

### 3.5. Member-2 - Dựng Solution 2 theo contract chung

Member-2 cần chốt sớm:
- Bộ parser cho free-text phải map được vào hard/soft/unsupported requirement.
- Rule-based ranking hoặc re-ranking phải trả ra cùng output schema với Solution 1.

Cách dựng:
- Bước 1: nhận `input` từ validation case.
- Bước 2: parse free-text và chạy pipeline Solution 2.
- Bước 3: map kết quả nội bộ sang output contract chung.
- Bước 4: ghi rõ unsupported requirement nếu case không đo lường được hoàn toàn.

### 3.6. Thứ tự phụ thuộc giữa các thành viên

Thứ tự làm việc nên là:
1. member-3 chốt schema dataset chung.
2. member-4 chốt validation case schema và output contract.
3. member-1 và member-2 dựng pipeline theo contract đó.
4. member-4 nhận output từ hai bên để chạy evaluation chung.

Nếu chưa chốt output contract mà member-1 hoặc member-2 đã code riêng, về sau rất dễ lệch format và mất thời gian nối pipeline.

## 4. Timeline 2 tuần

### Tuần 1 (29/06 – 05/07) — Phân công dataset + Thiết kế solution + Chuẩn bị validation
Việc cần làm:
- member-3 rà soát dataset chung đã có, chuẩn hóa schema hoặc ghi nhận các vấn đề dữ liệu nếu có.
- member-4 dựng validation set bản 1 và chốt output contract chung cho hai solution.
- member-1 và member-2 chốt input, output và pipeline tổng quát của solution mình dựa trên contract đó.
- Cả nhóm cùng rà soát khả năng triển khai thực tế của từng solution.
- Thống nhất tiêu chí đánh giá để so sánh hai solution.

Cuối tuần — Review chéo:
- Hai nhóm đánh giá chéo thiết kế pipeline, dataset chung và tập validation chung.
- Chốt dataset chung và tập validation chung để đảm bảo đánh giá toàn diện hơn.

Đầu ra:
1. Pipeline design của mỗi nhóm.
2. Dataset chung đã được rà soát và xác nhận có thể dùng cho cả hai solution.
3. Tập validation chung bản 1 đã được review.
4. Output contract chung cho hai solution đã được chốt.
5. Danh sách rủi ro/chặn kỹ thuật của từng nhóm.

### Tuần 2 (06/07 – 12/07) — Triển khai + Đánh giá + Chuẩn bị báo cáo
Việc cần làm:
- member-1 triển khai Solution 1 trên dataset chung.
- member-2 triển khai Solution 2 trên dataset chung.
- member-3 hỗ trợ xử lý các vấn đề dữ liệu nếu phát sinh khi chạy thử.
- member-4 chạy validation, tổng hợp kết quả đánh giá và đối chiếu giữa hai solution.
- Cả nhóm chạy thử trên cùng tập dataset chung và tập validation chung.
- So sánh kết quả ban đầu, tổng hợp điểm mạnh/yếu của từng solution.
- Chuẩn bị nội dung báo cáo, slide hoặc tài liệu xin ý kiến giảng viên.

Cuối tuần — Demo và chốt hướng:
- Mỗi nhóm demo bản hiện có của mình.
- Đánh giá độ khả thi và chất lượng của từng solution.
- Chốt hướng ưu tiên để tiếp tục phát triển hoặc trình bày.

Đầu ra:
1. Bản triển khai/demonstration của mỗi nhóm.
2. Kết quả đánh giá sơ bộ trên tập validation chung.
3. Bảng so sánh output của hai solution theo cùng contract chung.
4. Biên bản demo: tiến độ, rủi ro, hướng ưu tiên và kế hoạch tiếp theo.

## 5. Timeline chi tiết theo thành viên

### 5.1. Mốc phụ thuộc bắt buộc

Các mốc sau phải được chốt theo đúng thứ tự, nếu trễ sẽ chặn các thành viên khác:

1. member-3 phải chốt schema dataset chung trước khi member-4 khóa validation set.
2. member-4 phải chốt `validation case schema` và `output contract` trước khi member-1 và member-2 bắt đầu dựng pipeline chính thức.
3. member-1 và member-2 chỉ nên code phần export output sau khi contract chung đã khóa.
4. member-4 chỉ bắt đầu tổng hợp đánh giá sau khi cả hai solution đều xuất được output đúng schema.

### 5.2. Timeline member-3

#### Tuần 1
- `29/06 - 30/06`: rà soát dataset chung, kiểm tra cột bắt buộc, khóa định danh `property_id`, kiểu dữ liệu.
- `01/07`: xuất bản schema dataset chung và ghi chú dữ liệu thiếu/lỗi nếu có.
- `02/07`: trao đổi với member-4 để đảm bảo validation set dùng đúng tên cột và đúng format input.
- `03/07 - 05/07`: hỗ trợ member-1 và member-2 nếu phát hiện case nào không chạy được do lỗi dữ liệu.

Đầu ra bắt buộc trước `01/07`:
- Danh sách cột dùng chung.
- Quy ước field chính cho property.
- Ghi chú dữ liệu thiếu hoặc field không ổn định.

#### Tuần 2
- `06/07 - 08/07`: xử lý các vấn đề dữ liệu phát sinh khi hai solution chạy thử.
- `09/07 - 12/07`: khóa lại phiên bản dataset dùng cho demo/evaluation, tránh thay đổi giữa chừng.

### 5.3. Timeline member-4

#### Tuần 1
- `29/06`: đọc schema dataset chung hiện có và xem template validation hiện tại.
- `30/06`: phác thảo `validation case schema`.
- `01/07`: chốt `format input/output đánh giá` để member-1 và member-2 dựng pipeline theo cùng chuẩn.
- `02/07`: tạo `validation set bản 1` với số lượng case tối thiểu ban đầu.
- `03/07`: review chéo với member-1, member-2, member-3 để sửa field hoặc note chưa hợp lý.
- `04/07 - 05/07`: khóa `validation set bản 1` và khóa `output contract chung`.

Đầu ra bắt buộc:
- Trước `01/07`: phải có bản nháp `output contract`.
- Trong `01/07`: phải chốt bản contract đủ dùng để member-1 và member-2 bắt đầu dựng pipeline.
- Trước `05/07`: phải bàn giao `validation set bản 1` có thể chạy được ngay.

Nếu member-4 chưa chốt contract trước `01/07`, member-1 và member-2 chỉ nên dựng code nội bộ, chưa nên khóa format output.

#### Tuần 2
- `06/07 - 07/07`: nhận output chạy thử từ hai solution, kiểm tra đúng schema hay chưa.
- `08/07 - 10/07`: chạy validation, tổng hợp bảng so sánh, đánh dấu case lỗi hoặc case khó.
- `11/07 - 12/07`: chốt báo cáo đánh giá sơ bộ và nhận xét giữa hai solution.

### 5.4. Timeline member-1

#### Tuần 1
- `29/06 - 30/06`: thiết kế logic nội bộ của Solution 1.
- `01/07`: nhận `output contract` từ member-4 và map cấu trúc pipeline theo contract đó.
- `02/07 - 03/07`: dựng parser input theo validation schema và dựng output mapper.
- `04/07 - 05/07`: chạy thử với một số validation case bản 1, kiểm tra xuất đúng schema.

Đầu ra bắt buộc:
- Sau `01/07`: phải bám đúng `output contract chung`.
- Trước `05/07`: phải có bản pipeline xuất được ít nhất 1 kết quả mẫu đúng schema.

#### Tuần 2
- `06/07 - 09/07`: hoàn thiện pipeline chính của Solution 1.
- `10/07`: xuất kết quả trên validation set chung cho member-4.
- `11/07 - 12/07`: sửa lỗi theo phản hồi từ validation và chuẩn bị demo.

### 5.5. Timeline member-2

#### Tuần 1
- `29/06 - 30/06`: thiết kế logic nội bộ của Solution 2.
- `01/07`: nhận `output contract` từ member-4 và map pipeline theo contract đó.
- `02/07 - 03/07`: dựng parser free-text, parser hard/soft/unsupported và output mapper.
- `04/07 - 05/07`: chạy thử với một số validation case bản 1, kiểm tra xuất đúng schema.

Đầu ra bắt buộc:
- Sau `01/07`: phải bám đúng `output contract chung`.
- Trước `05/07`: phải có bản pipeline xuất được ít nhất 1 kết quả mẫu đúng schema.

#### Tuần 2
- `06/07 - 09/07`: hoàn thiện pipeline chính của Solution 2.
- `10/07`: xuất kết quả trên validation set chung cho member-4.
- `11/07 - 12/07`: sửa lỗi theo phản hồi từ validation và chuẩn bị demo.

### 5.6. Các điểm chốt cần có trước

Để tránh tắc việc, các mốc này phải có trước:

| Nội dung cần chốt trước | Người phụ trách | Hạn cuối | Người phụ thuộc |
|---|---|---|---|
| Schema dataset chung | member-3 | 01/07/2026 | member-4, member-1, member-2 |
| Output contract chung | member-4 | 01/07/2026 | member-1, member-2 |
| Validation set bản 1 | member-4 | 05/07/2026 | member-1, member-2, member-4 |
| Bản output mẫu đúng schema của Solution 1 | member-1 | 05/07/2026 | member-4 |
| Bản output mẫu đúng schema của Solution 2 | member-2 | 05/07/2026 | member-4 |
| Kết quả chạy full validation set | member-1, member-2 | 10/07/2026 | member-4 |
| Bảng so sánh đánh giá sơ bộ | member-4 | 12/07/2026 | cả nhóm |

## 6. Bảng deadline theo từng thành viên

### 6.1. Member-3 - Dataset chung

| Tuần | Mốc | Deadline gợi ý | Mục tiêu chính | Output cần có |
|---|---|---|---|---|
| Tuần 1 | M1.1 | 30/06/2026 | Rà soát dataset chung và kiểm tra field bắt buộc | Danh sách cột chính, `property_id`, các field dùng cho 2 solution |
| Tuần 1 | M1.2 | 01/07/2026 | Chốt schema dataset chung | Schema dataset chung đã khóa, note dữ liệu thiếu/lỗi |
| Tuần 1 | M1.3 | 03/07/2026 | Đồng bộ với member-4 về tên field và format input | Validation set dùng đúng cột và đúng quy ước field |
| Tuần 2 | M1.4 | 08/07/2026 | Hỗ trợ xử lý issue dữ liệu khi 2 solution chạy thử | Danh sách issue dữ liệu và cách xử lý đã thống nhất |
| Tuần 2 | M1.5 | 10/07/2026 | Khóa version dataset dùng cho demo/evaluation | Một phiên bản dataset ổn định để cả nhóm dùng chung |

### 6.2. Member-1 - Solution 1

| Tuần | Mốc | Deadline gợi ý | Mục tiêu chính | Output cần có |
|---|---|---|---|---|
| Tuần 1 | M2.1 | 30/06/2026 | Chốt logic nội bộ và pipeline tổng quát của Solution 1 | Sơ đồ pipeline hoặc mô tả các bước xử lý chính |
| Tuần 1 | M2.2 | 01/07/2026 | Nhận output contract từ member-4 và map pipeline theo chuẩn chung | Danh sách field input/output mà Solution 1 sẽ hỗ trợ |
| Tuần 1 | M2.3 | 03/07/2026 | Dựng parser input và output mapper theo contract | Hàm/module nhận input validation case và xuất đúng schema chung |
| Tuần 1 | M2.4 | 05/07/2026 | Chạy thử với validation set bản 1 | Ít nhất 1 output mẫu đúng schema cho Solution 1 |
| Tuần 2 | M2.5 | 09/07/2026 | Hoàn thiện pipeline chính của Solution 1 | Bản chạy được trên nhiều case của validation set |
| Tuần 2 | M2.6 | 10/07/2026 | Nộp kết quả chạy full validation set cho member-4 | File output đầy đủ theo contract chung |
| Tuần 2 | M2.7 | 12/07/2026 | Sửa lỗi theo phản hồi và chuẩn bị demo | Bản demo ổn định của Solution 1 |

### 6.3. Member-4 - Validation set và evaluation

| Tuần | Mốc | Deadline gợi ý | Mục tiêu chính | Output cần có |
|---|---|---|---|---|
| Tuần 1 | M3.1 | 30/06/2026 | Phác thảo validation case schema | Bản nháp cấu trúc 1 validation case |
| Tuần 1 | M3.2 | 01/07/2026 | Chốt format input/output đánh giá cho cả 2 solution | Output contract chung để member-1 và member-2 dựng pipeline |
| Tuần 1 | M3.3 | 02/07/2026 | Tạo validation set bản 1 | Một file validation set có thể chạy thử ngay |
| Tuần 1 | M3.4 | 05/07/2026 | Review và khóa validation set bản 1 | Validation set bản 1 + ghi chú review + case coverage tối thiểu |
| Tuần 2 | M3.5 | 07/07/2026 | Kiểm tra output chạy thử từ 2 solution có đúng schema không | Danh sách lỗi schema hoặc xác nhận pass schema |
| Tuần 2 | M3.6 | 10/07/2026 | Chạy evaluation và tổng hợp kết quả ban đầu | Bảng so sánh sơ bộ giữa Solution 1 và Solution 2 |
| Tuần 2 | M3.7 | 12/07/2026 | Chốt báo cáo đánh giá sơ bộ | Bảng đánh giá cuối tuần + nhận xét + case lỗi đáng chú ý |

### 6.4. Member-2 - Solution 2

| Tuần | Mốc | Deadline gợi ý | Mục tiêu chính | Output cần có |
|---|---|---|---|---|
| Tuần 1 | M4.1 | 30/06/2026 | Chốt logic nội bộ và pipeline tổng quát của Solution 2 | Sơ đồ pipeline hoặc mô tả các bước xử lý chính |
| Tuần 1 | M4.2 | 01/07/2026 | Nhận output contract từ member-4 và map pipeline theo chuẩn chung | Danh sách field input/output mà Solution 2 sẽ hỗ trợ |
| Tuần 1 | M4.3 | 03/07/2026 | Dựng parser free-text, hard/soft/unsupported và output mapper | Hàm/module xử lý free-text và xuất đúng schema chung |
| Tuần 1 | M4.4 | 05/07/2026 | Chạy thử với validation set bản 1 | Ít nhất 1 output mẫu đúng schema cho Solution 2 |
| Tuần 2 | M4.5 | 09/07/2026 | Hoàn thiện pipeline chính của Solution 2 | Bản chạy được trên nhiều case của validation set |
| Tuần 2 | M4.6 | 10/07/2026 | Nộp kết quả chạy full validation set cho member-4 | File output đầy đủ theo contract chung |
| Tuần 2 | M4.7 | 12/07/2026 | Sửa lỗi theo phản hồi và chuẩn bị demo | Bản demo ổn định của Solution 2 |

## 7. Bảng theo dõi tiến độ tổng quan

| Tuần | Thời gian | Sự kiện cuối tuần | Đầu ra bắt buộc | Trạng thái |
|---|---|---|---|---|
| Tuần 1 | 29/06 – 05/07 | Review chéo pipeline + validation set | Pipeline design + rà soát dataset chung + validation set bản 1 + output contract chung + danh sách rủi ro | Planned |
| Tuần 2 | 06/07 – 12/07 | Demo và chốt hướng | Bản triển khai/demonstration + kết quả đánh giá sơ bộ + bảng so sánh output chung + biên bản demo | Planned |

## 8. Bảng theo dõi tiến độ theo thành viên

| Thành viên | Tuần 1 | Tuần 2 | Ghi chú |
|---|---|---|---|
| member-1 | Thiết kế Solution 1 theo output contract chung | Triển khai/demonstrate Solution 1 và xuất output đúng schema | Solution 1 |
| member-2 | Thiết kế Solution 2 theo output contract chung | Triển khai/demonstrate Solution 2 và xuất output đúng schema | Solution 2 |
| member-3 | Rà soát schema/cột bắt buộc của dataset chung | Hỗ trợ xử lý vấn đề dữ liệu khi chạy thử | Dataset dùng chung |
| member-4 | Dựng validation set bản 1 + chốt output contract + tiêu chí đánh giá | Chạy validation, tổng hợp bảng so sánh kết quả | Validation dùng chung |

## 9. Quy ước cập nhật
- **Planned**: đã nhận việc, chưa hoàn tất.
- **Done**: đã hoàn tất đầu ra và đã nghiệm thu.
- **Blocked**: đang vướng, cần hỗ trợ.

## 10. Cơ chế kiểm soát
1. Mỗi thành viên cập nhật trạng thái trước checkpoint cuối tuần.
2. Nếu đầu ra tuần chưa đạt: phải có kế hoạch bù trong 48 giờ.
3. Chỉ chuyển sang tuần tiếp theo khi đầu ra bắt buộc đã được nghiệm thu nội bộ.
4. Không thay đổi output contract sau khi member-1 và member-2 đã bắt đầu code, trừ khi cả nhóm cùng đồng ý.

## 11. Ngoài phạm vi
- Không quy định công nghệ/cú pháp kỹ thuật cụ thể.
- Không ép buộc hai solution phải dùng cùng kỹ thuật nội bộ.
- Không ràng buộc chi tiết theo ngày, chỉ chốt theo deadline tuần.
