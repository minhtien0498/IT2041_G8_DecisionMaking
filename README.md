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
│   └── validation_analysis.ipynb # Notebook phân tích data validation
├── tests/                    # Các bộ unit test kiểm định mã nguồn
├── src/                      # Thư mục mã nguồn chính (Python Package)
│   ├── __init__.py
│   ├── data/                 # Modules thu thập & tiền xử lý dữ liệu
│   │   ├── __init__.py
│   │   └── prepare_data.py   # Lọc và làm sạch BĐS Quận Gò Vấp từ file CSV gốc
│   ├── demo/                 # Modules chạy kịch bản & giao diện demo
│   │   ├── __init__.py
│   │   └── run_pipeline.py   # Chạy pipeline tính điểm & đề xuất Top 5
│   ├── eval/                 # Modules đánh giá thuật toán
│   │   ├── __init__.py
│   │   ├── generate_validation_set.py # Sinh 50 synthetic validation scenarios
│   │   └── evaluate_pipeline.py       # Tính CSR, Precision/Recall@K, NDCG, MAP
│   └── models/               # Modules lưu trữ/gọi mô hình (LLMs)
│       └── __init__.py
├── data/                     # Dữ liệu phục vụ hệ thống (.json)
│   ├── go_vap_30.json        # 37 BĐS Gò Vấp sạch sau khi lọc
│   ├── go_vap_enriched.json  # Dữ liệu BĐS đã làm giàu tọa độ POI
│   └── validation_50_scenarios.json # 50 kịch bản kiểm thử synthetic
├── docs/                     # Tài liệu nghiên cứu & phân tích
│   ├── dataset_recommendation.md
│   ├── data_preparation_plan.md
│   ├── solution_evaluation.md
│   └── source_notes/         # Tài liệu nháp & chi tiết giải thuật cũ
├── outputs/                  # Kết quả xuất ra từ các pipeline
│   ├── solution1_results.json
│   ├── validation_report.md
│   ├── validation_summary.json
│   └── preliminary_results.md # Báo cáo kết quả sơ khởi gửi giáo viên
├── survey/                   # Giao diện khảo sát nhu cầu người dùng
│   └── index.html
├── archive/                  # [ĐÃ IGNORE] Code và tài liệu của đề tài cũ
└── .gitignore                # Quản lý các file không commit lên git (data lớn, .DS_Store,...)
```

---

## 🚀 Hướng dẫn chạy Pipeline Sơ Khởi (Midterm)

Hệ thống hiện tại chạy trên tập dữ liệu mẫu gồm **37 BĐS sạch tại Quận Gò Vấp**, đã tích hợp tính toán khoảng cách thực tế (theo công thức Haversine) đến các POI chính (Trường học, Công viên, Bệnh viện, Siêu thị, Trục đường lớn).

### 1. Trích xuất dữ liệu Gò Vấp
Chạy script lọc dữ liệu từ file csv gốc:
```bash
python3 src/data/prepare_data.py
```
*Output:* Tạo ra file `data/go_vap_30.json` chứa thông tin BĐS đã làm sạch.

### 2. Chạy Pipeline tính điểm & tìm Top 5
Chạy pipeline đánh giá theo 3 kịch bản người dùng (Gia đình có con nhỏ, Người trẻ độc thân, Nhà đầu tư):
```bash
python3 src/demo/run_pipeline.py
```
*Output:*
- `data/go_vap_enriched.json`: Dữ liệu đã enrich khoảng cách POI.
- `outputs/solution1_results.json`: Kết quả chi tiết điểm số của các kịch bản.

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

### Kết quả validation hiện tại

Trên tập **37 BĐS Gò Vấp** và **50 synthetic scenarios**:

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

## 📊 Kết quả sơ khởi (Midterm 13/6)

Chi tiết kết quả chạy thử nghiệm và phương pháp đánh giá có thể xem trực tiếp tại file:
👉 **[outputs/preliminary_results.md](file:///Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/outputs/preliminary_results.md)**
