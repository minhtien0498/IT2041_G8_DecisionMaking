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
│   │   └── __init__.py
│   └── models/               # Modules lưu trữ/gọi mô hình (LLMs)
│       └── __init__.py
├── data/                     # Dữ liệu phục vụ hệ thống (.json)
│   ├── go_vap_30.json        # 37 BĐS Gò Vấp sạch sau khi lọc
│   └── go_vap_enriched.json  # Dữ liệu BĐS đã làm giàu tọa độ POI
├── docs/                     # Tài liệu nghiên cứu & phân tích
│   ├── dataset_recommendation.md
│   ├── data_preparation_plan.md
│   ├── solution_evaluation.md
│   └── source_notes/         # Tài liệu nháp & chi tiết giải thuật cũ
├── outputs/                  # Kết quả xuất ra từ các pipeline
│   ├── pipeline_5_1_results.json
│   └── preliminary_results.md # Báo cáo kết quả sơ khởi gửi giáo viên
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
- `outputs/pipeline_5_1_results.json`: Kết quả chi tiết điểm số của các kịch bản.

---

## 📊 Kết quả sơ khởi (Midterm 13/6)

Chi tiết kết quả chạy thử nghiệm và phương pháp đánh giá có thể xem trực tiếp tại file:
👉 **[outputs/preliminary_results.md](file:///Users/totien/Documents/caohoc/Ki2-2026/IT2041_G8_DecisionMaking/outputs/preliminary_results.md)**
