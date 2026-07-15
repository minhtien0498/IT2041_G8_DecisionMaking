# IT2041 G8 Decision Making - Real Estate Advisory System

Repository này chứa mã nguồn và tài liệu của **Nhóm 8 (IT2041)** cho đề tài:
**Hệ thống tư vấn chọn bất động sản thông minh ở TP.HCM (Smart Real Estate Advisory System)**.

---

## 📂 Cấu trúc thư mục chuẩn hóa (Standardized Layout)

```text
IT2041_G8_DecisionMaking/
├── README.md                 # Tài liệu hướng dẫn chính của dự án
├── PROJECT_PLAN.md           # Kế hoạch phát triển dự án chi tiết
├── requirements.txt          # Khai báo các thư viện Python phụ thuộc
├── configs/                  # Lưu trữ cấu hình hệ thống
├── notebooks/                # Jupyter Notebooks nghiên cứu thuật toán
│   ├── pipeline_demo.ipynb
│   ├── enrich_gv_tb_100_overpass_pipeline.ipynb  # Enrich bằng Overpass API
│   ├── enrich_gv_tb_100_geoapify_pipeline.ipynb  # Enrich bằng Geoapify Places API
│   ├── enrich_gv_tb_100_mapbox_pipeline.ipynb    # Enrich bằng Mapbox API
│   └── validation_analysis.ipynb # Notebook phân tích data validation
├── tests/                    # Các bộ unit test kiểm định mã nguồn
├── src/                      # Thư mục mã nguồn chính (Python Package)
│   ├── __init__.py
│   ├── data/                 # Modules thu thập & tiền xử lý dữ liệu
│   │   ├── __init__.py
│   │   ├── prepare_data.py   # Script legacy cho bộ Gò Vấp cũ
│   │   ├── prepare_gv_tb_100.py # Tạo bộ clean dataset 100 căn
│   │   └── enrich_gv_tb_100.py  # Enrich POI cho bộ 100 căn
│   ├── demo/                 # Modules chạy kịch bản & giao diện demo
│   │   ├── __init__.py
│   │   └── run_solution2.py  # Demo hiện tại cho Solution 2
│   ├── eval/                 # Modules đánh giá thuật toán
│   │   ├── __init__.py
│   │   ├── generate_validation_set.py # Sinh 50 synthetic validation scenarios
│   │   └── evaluate_pipeline.py       # Tính CSR, Precision/Recall@K, NDCG, MAP
│   └── models/               # Modules lưu trữ/gọi mô hình (LLMs)
│       └── __init__.py
├── data/                     # Dữ liệu phục vụ hệ thống (.json)
│   ├── raw/
│   │   ├── data_public.csv
│   │   └── vietnam_housing_dataset.csv
│   ├── overpass/             # Output, checkpoint, schema, curl mẫu cho Overpass API
│   ├── geoapify/             # Output, checkpoint, schema, curl mẫu cho Geoapify API
│   ├── mapbox/               # Output, checkpoint, schema, curl mẫu cho Mapbox API
│   ├── go_vap_tan_binh_100.json
│   ├── go_vap_tan_binh_100_enriched.json
│   ├── go_vap_30.json        # Bộ legacy
│   ├── go_vap_enriched.json  # Bộ legacy
│   └── validation_50_scenarios.json # 50 kịch bản kiểm thử synthetic
├── docs/                     # Tài liệu nghiên cứu & phân tích
│   ├── dataset_recommendation.md
│   ├── data_preparation_plan.md
│   ├── solution_evaluation.md
│   └── source_notes/         # Tài liệu nháp & chi tiết giải thuật cũ
├── outputs/                  # Kết quả xuất ra từ các pipeline
│   ├── validation_report.md
│   ├── validation_summary.json
│   └── preliminary_results.md # Ghi chú chuyển tiếp giữa baseline cũ và workflow hiện tại
├── survey/                   # Giao diện khảo sát nhu cầu người dùng
│   └── index.html
├── archive/                  # [ĐÃ IGNORE] Code và tài liệu của đề tài cũ
└── .gitignore                # Quản lý các file không commit lên git (data lớn, .DS_Store,...)
```

---

## 🚀 Hướng dẫn chuẩn bị dataset 100 căn

Workflow dữ liệu hiện tại của nhóm đã chuyển sang bộ **100 BĐS** gồm:
- `50` căn ở **Gò Vấp**
- `50` căn ở **Tân Bình**

Luồng chuẩn hiện tại là:
1. tạo bộ clean dataset `100` căn từ file nguồn
2. enrich khoảng cách POI cho bộ `100` căn
3. dùng file enriched này để chuẩn bị bước migrate pipeline/validation sang scope mới

### 1. Tạo bộ clean dataset 100 căn
Chạy script lọc dữ liệu từ file CSV gốc:
```bash
python3 src/data/prepare_gv_tb_100.py
```
*Output:* Tạo ra file `data/go_vap_tan_binh_100.json`.

Nếu muốn thao tác trực quan theo từng bước:
```bash
notebooks/prepare_gv_tb_100.ipynb
```

### 2. Ghi chú về pipeline hiện tại

- Bộ `100` căn đã sẵn sàng ở mức `clean` và `enriched`.
- Một số script demo/validation cũ trong repo vẫn đang tham chiếu bộ `legacy` (`go_vap_30.json`, `go_vap_enriched.json`).
- Bước tiếp theo là chuyển hẳn pipeline và validation sang `go_vap_tan_binh_100_enriched.json`.

---

## 🌐 Enrich Bằng API

Ngoài file enrich thủ công cũ, repo hiện đã có 3 notebook enrich bằng API thật:

- [notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb](notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb)
- [notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb](notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb)
- [notebooks/enrich_gv_tb_100_mapbox_pipeline.ipynb](notebooks/enrich_gv_tb_100_mapbox_pipeline.ipynb)

Các notebook này đều:
- đọc input từ [data/go_vap_tan_binh_100.json](data/go_vap_tan_binh_100.json)
- enrich theo batch
- có `checkpoint`
- có `error log`
- sinh output JSON dùng lại cho pipeline khác

Ghi chú định hướng hiện tại: `Mapbox` là provider được ưu tiên để cả Solution 1 và Solution 2 dùng chung cho enrichment final; `Overpass` và `Geoapify` vẫn giữ vai trò baseline/đối chiếu vì đã có output và so sánh trước đó.

### 1. Overpass API

Notebook:
- [notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb](notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb)

Thư mục output:
- [data/overpass](data/overpass)

Các file chính:
- Output: [data/overpass/go_vap_tan_binh_100_enriched_overpass_api.json](data/overpass/go_vap_tan_binh_100_enriched_overpass_api.json)
- Checkpoint: [data/overpass/go_vap_tan_binh_100_enriched_overpass_api_checkpoint.json](data/overpass/go_vap_tan_binh_100_enriched_overpass_api_checkpoint.json)
- Error log: [data/overpass/go_vap_tan_binh_100_overpass_errors.json](data/overpass/go_vap_tan_binh_100_overpass_errors.json)
- Schema readme: [data/overpass/overpass_enriched_schema_readme.json](data/overpass/overpass_enriched_schema_readme.json)
- cURL/Postman mẫu: [data/overpass/overpass_api_curl_examples.md](data/overpass/overpass_api_curl_examples.md)

### 2. Geoapify Places API

Notebook:
- [notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb](notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb)

Thư mục output:
- [data/geoapify](data/geoapify)

Các file chính:
- Output: [data/geoapify/go_vap_tan_binh_100_enriched_geoapify_api.json](data/geoapify/go_vap_tan_binh_100_enriched_geoapify_api.json)
- Checkpoint: [data/geoapify/go_vap_tan_binh_100_enriched_geoapify_api_checkpoint.json](data/geoapify/go_vap_tan_binh_100_enriched_geoapify_api_checkpoint.json)
- Error log: [data/geoapify/go_vap_tan_binh_100_geoapify_errors.json](data/geoapify/go_vap_tan_binh_100_geoapify_errors.json)
- Schema readme: [data/geoapify/geoapify_enriched_schema_readme.json](data/geoapify/geoapify_enriched_schema_readme.json)
- cURL/Postman mẫu: [data/geoapify/geoapify_api_curl_examples.md](data/geoapify/geoapify_api_curl_examples.md)

### 3. Mapbox API

Notebook:
- [notebooks/enrich_gv_tb_100_mapbox_pipeline.ipynb](notebooks/enrich_gv_tb_100_mapbox_pipeline.ipynb)

Script:
- [src/data/enrich_gv_tb_100_mapbox.py](src/data/enrich_gv_tb_100_mapbox.py)

Thư mục output:
- [data/mapbox](data/mapbox)

Các file chính:
- Output: [data/mapbox/go_vap_tan_binh_100_enriched_mapbox_api.json](data/mapbox/go_vap_tan_binh_100_enriched_mapbox_api.json)
- Checkpoint: [data/mapbox/go_vap_tan_binh_100_enriched_mapbox_api_checkpoint.json](data/mapbox/go_vap_tan_binh_100_enriched_mapbox_api_checkpoint.json)
- Error log: [data/mapbox/go_vap_tan_binh_100_mapbox_errors.json](data/mapbox/go_vap_tan_binh_100_mapbox_errors.json)
- Schema readme: [data/mapbox/mapbox_enriched_schema_readme.json](data/mapbox/mapbox_enriched_schema_readme.json)
- cURL/Postman mẫu: [data/mapbox/mapbox_api_curl_examples.md](data/mapbox/mapbox_api_curl_examples.md)

Chạy nhanh bằng script:

```bash
python3 src/data/enrich_gv_tb_100_mapbox.py
```

Smoke test 3 mẫu đầu:

```bash
python3 src/data/enrich_gv_tb_100_mapbox.py --max-records 3
```

### 4. Hướng dẫn tạo `GEOAPIFY_API_KEY`

1. Đăng ký tài khoản:
Miễn phí, không yêu cầu thẻ tín dụng. Truy cập trang [Geoapify MyProjects](https://myprojects.geoapify.com/) và tạo một tài khoản mới. Có thể đăng nhập nhanh bằng Google hoặc GitHub.

2. Tạo dự án mới:
Sau khi đăng nhập vào Dashboard, nhấn vào nút `Create a new project`. Đặt tên dự án sao cho dễ quản lý, ví dụ: `location-verification-service`.

3. Sao chép API Key:
Vào mục `API Keys` bên trong dự án vừa tạo. Geoapify đã tự động tạo sẵn một API key đầu tiên cho bạn. Bấm `Copy` để lấy chuỗi mã này. Đây chính là giá trị để thay thế cho `YOUR_GEOAPIFY_API_KEY`.

### 5. Cấu hình `.env`

Repo đã có file mẫu:
- [.env.example](.env.example)

Tạo file `.env` ở thư mục gốc project với nội dung:

```bash
GEOAPIFY_API_KEY=your_real_geoapify_api_key
MAPBOX_TOKEN=your_real_mapbox_token
```

Hoặc export trực tiếp trong shell:

```bash
export GEOAPIFY_API_KEY="your_real_geoapify_api_key"
export MAPBOX_TOKEN="your_real_mapbox_token"
```

### 6. Cách chạy notebook mới

Chạy Overpass:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb
```

Chạy Geoapify:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb
```

Chạy Mapbox:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/enrich_gv_tb_100_mapbox_pipeline.ipynb
```

Hoặc mở trực tiếp bằng Jupyter và chạy theo cell.

### 7. So sánh provider

File tổng hợp hiện tại:
- [docs/provider_comparison_overpass_vs_geoapify.md](docs/provider_comparison_overpass_vs_geoapify.md)

File này so sánh nhanh:
- giá cả / quota / limit
- tốc độ và thời gian chạy quan sát được
- độ đầy dữ liệu
- độ ổn định khi chạy notebook

---

## 🧪 Hướng dẫn chạy Validation

Validation hiện tại gồm 2 phần:

1. **Synthetic Scenario Validation**: kiểm thử kỹ thuật bằng 50 kịch bản nhu cầu người dùng được sinh bằng code.
2. **Human-labeled Validation**: hướng cần bổ sung bằng khảo sát người dùng thật để đánh giá chất lượng ra quyết định của DSS.

Notebook hỗ trợ trình bày validation:

```text
notebooks/validation_analysis.ipynb
```

Notebook này đọc lại `validation_50_scenarios.json` và `validation_summary.json` để hiển thị metric, chart theo archetype, edge cases và phần nhận xét giới hạn của synthetic validation.

### 1. Sinh bộ 50 validation scenarios

```bash
python3 src/eval/generate_validation_set.py
```

*Output:* Tạo/cập nhật file `data/validation_50_scenarios.json`.

Bộ scenario này bao phủ 5 archetype:
- Gia đình có con nhỏ.
- Người trẻ / young professional.
- Nhà đầu tư.
- Người cao tuổi.
- Cặp đôi.

### 2. Chạy đánh giá pipeline

```bash
python3 src/eval/evaluate_pipeline.py
```

*Output:*
- `outputs/validation_report.md`: Báo cáo validation chi tiết.
- `outputs/validation_summary.json`: Kết quả metric dạng JSON.

Các metric đang dùng:
- Constraint Satisfaction Rate (CSR).
- Precision@3, Precision@5.
- Recall@3, Recall@5.
- NDCG@3, NDCG@5.
- Mean Average Precision (MAP).
- Breakdown theo archetype và edge cases.

### Ghi chú đổi scope solution

- `Solution 1` cũ dạng rule-based đã bị loại khỏi scope final vì quá đơn giản.
- `Solution 1` hiện tại là pipeline tuần tự hai LLM có guardrail của Phú.
- `Solution 2` giữ nguyên là hướng hybrid của Quang.
- Xem thêm: [docs/notes/solution_scope_change_2026-07-11.md](docs/notes/solution_scope_change_2026-07-11.md)

### Kết quả validation hiện tại

Các metric dưới đây là **baseline legacy** trên tập **37 BĐS Gò Vấp** và **50 synthetic scenarios**. Chúng chưa phải kết quả rerun trên bộ `100` căn mới:

| Metric | Giá trị |
|---|---:|
| CSR | 100.0% |
| Precision@5 | 76.8% |
| Recall@5 | 92.0% |
| NDCG@5 | 0.9200 |
| MAP | 0.9200 |

Lưu ý: `validation_50_scenarios.json` là **synthetic validation set**. Ground truth Top 5 được sinh từ reference scorer, nên bộ này phù hợp để kiểm tra độ ổn định, edge cases và tính nhất quán của pipeline. Để đánh giá recommendation có đúng với nhu cầu thật hay không, nhóm cần bổ sung **human-labeled validation set** từ khảo sát người dùng.

---

## 📝 Khảo sát người dùng cho DSS Validation

Giao diện khảo sát nằm tại:

```text
survey/index.html
```

Mục tiêu khảo sát:
- Thu thập ngân sách tối đa.
- Thu thập số phòng ngủ tối thiểu.
- Thu thập mức ưu tiên 1-5 cho trường học, công viên, bệnh viện, siêu thị, giao thông.
- Thu thập nhu cầu tự nhiên bằng văn bản.

Kết quả khảo sát nên được chuyển thành file validation độc lập, ví dụ:

```text
data/user_preference_validation.json
```

Đây sẽ là phần quan trọng để chứng minh chất lượng ra quyết định của hệ thống trong môn DSS with Data.

---

## 📊 Kết quả sơ khởi / Tài liệu tham chiếu cũ

File dưới đây là **kết quả baseline legacy của midterm**, được chạy trên bộ dữ liệu cũ `37` căn ở Gò Vấp:

👉 **[outputs/preliminary_results.md](outputs/preliminary_results.md)**

Lưu ý:
- File này được giữ lại để tham chiếu lịch sử phát triển của project.
- Nó **không đại diện cho workflow dữ liệu hiện tại** của nhóm, mà là ghi chú chuyển tiếp giữa bản cũ và bản mới.
- Workflow hiện tại đã chuyển sang bộ `100` căn:
  - `data/go_vap_tan_binh_100.json`
  - `data/go_vap_tan_binh_100_enriched.json`
- Khi migrate xong pipeline/validation sang bộ mới, nhóm nên tạo một báo cáo kết quả mới thay cho baseline midterm này.
