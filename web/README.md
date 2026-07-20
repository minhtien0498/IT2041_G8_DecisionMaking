# Web Demo Runbook

Tài liệu này mô tả các bước chuẩn bị, chạy web demo và các kịch bản test chính cho hệ thống tư vấn BĐS của nhóm.

Nếu muốn chạy theo từng cell trong Jupyter, dùng notebook:

```text
web/web_demo_steps.ipynb
```

## 1. Mục tiêu web demo

Web demo hỗ trợ hai nhóm tính năng:

- Nhập nhu cầu người dùng, chọn `Solution 1`, `Solution 2` hoặc `Cả hai`, sau đó trả về Top X bất động sản.
- Đánh giá kết quả bằng validation set nếu có ground truth, hoặc bằng rubric chấm tay khi chưa có validation set phù hợp.

## 2. Prerequisites

Yêu cầu máy local có:

- Python 3.11 hoặc tương đương.
- Docker Desktop đang chạy.
- Internet nếu test `Solution 1` hoặc free-text của `Solution 2` cần gọi API ngoài.
- File dữ liệu `data/go_vap_tan_binh_100_enriched.json`.
- File validation `data/validation_cases_v1.json` và/hoặc `data/validation_50_scenarios.json`.

## 3. Cấu hình môi trường

Tạo hoặc cập nhật file `.env` ở root project:

```bash
GEOAPIFY_API_KEY=your_geoapify_api_key
MAPBOX_TOKEN=your_mapbox_public_token
OPENROUTER_API_KEYS=your_openrouter_key
SOLUTION1_DB_DSN=postgresql://solution1:solution1@localhost:5433/solution1
```

Ghi chú:

- `.env` đã nằm trong `.gitignore`, không commit API key.
- `Solution 2` có thể chạy recommendation cơ bản chỉ với dataset local.
- `Solution 1` cần cả `OPENROUTER_API_KEYS` và Postgres.

## 4. Cài dependencies

```bash
pip install -r requirements.txt
```

Nếu muốn chạy test suite bằng `pytest`, cài thêm:

```bash
pip install pytest
```

## 5. Start services

Start Postgres cho `Solution 1`:

```bash
docker compose up -d solution1_db
```

Kiểm tra container:

```bash
docker compose ps
```

Kỳ vọng thấy `solution1_postgres` ở trạng thái `healthy`, port `5433`.

Start web:

```bash
uvicorn web.app:app --reload --port 8001
```

Mở trình duyệt:

```text
http://127.0.0.1:8001
```

Nếu muốn dùng port `8000`:

```bash
uvicorn web.app:app --reload --port 8000
```

Nếu báo `Address already in use`, đổi sang port khác như `8001`.

## 6. Health checks

Kiểm tra frontend:

```bash
curl -s -o /tmp/web_root.html -w '%{http_code}\n' http://127.0.0.1:8001/
```

Kỳ vọng:

```text
200
```

Kiểm tra validation cases:

```bash
curl -s http://127.0.0.1:8001/api/validation-cases
```

Kỳ vọng response có:

- `dataset = validation_cases_v1`
- danh sách `cases`
- case đầu thường là `V1_001`

## 7. Kịch bản test nhanh

### TC-01: Solution 2 trả Top 5

Thao tác trên UI:

- Chọn `S2`.
- Top X = `5`.
- Ngân sách = `8000`.
- Phòng ngủ tối thiểu = `3`.
- Nhu cầu tự do: `Gia đình có 2 con nhỏ, ưu tiên gần trường và công viên.`
- Nhấn `Chạy recommendation`.

Kỳ vọng:

- Status `ok`.
- Có 5 kết quả.
- Với dữ liệu hiện tại, Top IDs quan sát được:

```text
GV_010, GV_008, GV_013, GV_015, GV_026
```

### TC-02: Đánh giá kết quả hiện tại

Thao tác trên UI:

- Dùng cùng input của TC-01.
- Nhấn `Đánh giá kết quả này`.

Kỳ vọng:

- `Hard pass = 100%`.
- Nếu có expected priorities tương ứng, `Priority coverage` hiển thị phần trăm khớp.
- Nếu không có `ground_truth_top5`, phần IR metrics như Precision@K/NDCG@K sẽ hiển thị `N/A`.
- UI vẫn hiển thị human rubric: `relevance`, `constraint_fit`, `explainability`, `diversity`, `trust`.

### TC-03: Batch validation trên validation_cases_v1

Thao tác trên UI:

- Chọn dataset `validation_cases_v1`.
- Số case batch = `5`.
- Chọn `S2`.
- Nhấn `Batch validation`.

Kỳ vọng đã test local:

```text
solution2_hard_pass = 1.0
solution2_priority_coverage = 0.6667
cases = V1_001, V1_002, V1_003, V1_004, V1_005
```

### TC-04: Solution 1 kiểm tra DB không gọi LLM

Mục tiêu: xác nhận web kết nối được Postgres và load dataset cho `Solution 1`.

Gọi API với điều kiện bất khả thi:

```bash
curl -s http://127.0.0.1:8001/api/recommend \
  -H 'Content-Type: application/json' \
  -d '{
    "form": {
      "budget_max_million": 1,
      "min_bedrooms": 99,
      "soft_preferences": {
        "price": {"weight": 1.0, "direction": "lower_better", "min": 0, "max": 1}
      },
      "user_need_text": "Case test DB: không có nhà nào phù hợp."
    },
    "free_text": "Case test DB: không có nhà nào phù hợp.",
    "solution": "solution1",
    "top_x": 3
  }'
```

Kỳ vọng:

```text
status = no_candidate
top5 = []
explanation_summary = Không có bất động sản nào thỏa điều kiện lọc cứng từ form.
```

### TC-05: Solution 1 full LLM

Thao tác trên UI:

- Chọn `S1` hoặc `Cả hai`.
- Dùng input thực tế có candidate, ví dụ TC-01.
- Nhấn `Chạy recommendation`.

Kỳ vọng:

- Nếu OpenRouter key còn quota và model free phản hồi ổn, status `ok` và có Top X.
- Nếu OpenRouter chậm/rate-limit/quota lỗi, status `error` và message trả về trong card `SOLUTION1`.

Lưu ý test local gần nhất:

- DB đã healthy.
- `Solution 1` case `no_candidate` pass.
- Request `Solution 1` full LLM có thể vượt 90 giây với model free của OpenRouter, nên không nên dùng làm smoke test bắt buộc trước demo.

## 8. API endpoints

Các endpoint chính:

- `GET /`: frontend web.
- `GET /api/validation-cases?dataset=validation_cases_v1`: danh sách validation case.
- `POST /api/recommend`: chạy recommendation.
- `POST /api/validate`: chạy recommendation và đánh giá một input.
- `POST /api/validate-batch`: chạy batch validation.

Payload tối thiểu cho `POST /api/recommend`:

```json
{
  "form": {
    "budget_max_million": 8000,
    "min_bedrooms": 3,
    "soft_preferences": {
      "price": {"weight": 0.25, "direction": "lower_better", "min": 3000, "max": 8000},
      "distance_to_nearest_school_m": {"weight": 0.25, "direction": "lower_better", "min": 0, "max": 2000}
    },
    "user_need_text": "Gia đình ưu tiên gần trường."
  },
  "free_text": "Gia đình ưu tiên gần trường.",
  "solution": "solution2",
  "top_x": 5
}
```

## 9. Troubleshooting

### Docker daemon chưa chạy

Lỗi thường gặp:

```text
Cannot connect to the Docker daemon
```

Cách xử lý:

- Mở Docker Desktop.
- Chạy lại `docker compose up -d solution1_db`.

### Postgres chưa sẵn sàng

Lỗi trên UI:

```text
Solution 1 chưa kết nối được Postgres. Hãy mở Docker Desktop rồi chạy `docker compose up -d solution1_db`.
```

Cách xử lý:

```bash
docker compose ps
docker compose up -d solution1_db
```

### Port web bị chiếm

Lỗi:

```text
Address already in use
```

Cách xử lý:

```bash
uvicorn web.app:app --reload --port 8001
```

### Thiếu pytest

Lỗi:

```text
No module named pytest
```

Cách xử lý:

```bash
pip install pytest
python3 -m pytest -q
```

### Solution 1 chậm hoặc lỗi OpenRouter

Nguyên nhân có thể:

- Model free đang chậm.
- API key hết quota hoặc bị rate limit.
- Network tới OpenRouter không ổn định.

Cách xử lý:

- Test DB trước bằng TC-04.
- Demo chính bằng `Solution 2`.
- Chỉ bật `Solution 1` full LLM khi có thời gian chờ và key ổn định.
