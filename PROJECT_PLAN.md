# Kế hoạch thực hiện dự án - Nhóm 8 (IT2041)

## 📌 Tổng quan đề tài
**Đề tài**: Hệ thống tư vấn chọn bất động sản thông minh ở TP.HCM (Smart Real Estate Advisory System).
**Mục tiêu**: Hỗ trợ người dùng tìm kiếm, đánh giá và lựa chọn bất động sản phù hợp với nhu cầu cá nhân thông qua việc kết hợp cơ sở dữ liệu bất động sản, dữ liệu khoảng cách tiện ích (POI) và mô hình ngôn ngữ lớn (LLM).

---

## 📅 Lịch trình phát triển (Roadmap)

### 🔹 Pha 1: Midterm (Hoàn thành trước 13/6) - Pipeline 5.1
* [x] **Chuẩn hóa dữ liệu**: Lọc subset 37 BĐS "Nhà riêng" chất lượng cao tại Quận Gò Vấp từ tập dữ liệu gốc (HCMC 2025).
* [x] **Làm giàu dữ liệu (POI Enrichment)**: Tích hợp cơ sở dữ liệu các địa điểm tiện ích thực tế tại Gò Vấp (Trường học, Công viên, Bệnh viện, Siêu thị, Đường lớn) và tính toán khoảng cách thực (Haversine).
* [x] **Xây dựng bộ lọc cứng (Rule-based Filtering)**: Loại bỏ các BĐS vi phạm ràng buộc về Ngân sách tối đa hoặc số Phòng ngủ tối thiểu.
* [x] **Xây dựng bộ tính điểm (Rule-based Scoring)**: Thiết lập bộ trọng số chuẩn hóa theo 3 scenarios người dùng mẫu:
  1. *Gia đình có con nhỏ*: Ưu tiên trường học, công viên, siêu thị.
  2. *Người trẻ độc thân*: Ưu tiên giá rẻ, gần siêu thị, gần trục đường lớn.
  3. *Nhà đầu tư*: Ưu tiên giá/m² thấp, gần đường lớn, diện tích lớn.
* [x] **Đánh giá sơ bộ**: Viết báo cáo kết quả chạy pipeline và kiểm định tính đúng đắn của giải thuật.

### 🔹 Pha 2: Final (Sau Midterm) - Pipeline 5.2
* [ ] **Tích hợp API thực tế**: Gọi OpenStreetMap (OSM) hoặc Google Places API để lấy dữ liệu tiện ích tự động dựa trên tọa độ thật của từng listing BĐS.
* [ ] **Mở rộng dữ liệu**: Áp dụng pipeline trên quy mô lớn hơn (toàn TP.HCM hoặc 3-4 quận trung tâm/cận trung tâm, nâng quy mô lên 200-500 listings).
* [ ] **Tích hợp LLM (Requirement Parsing & Re-ranking)**:
  * LLM parse nhu cầu tự do của người dùng (ví dụ: "Tôi muốn tìm nhà yên tĩnh, gần chùa, ngân sách tầm 6 tỷ") thành các trọng số/ràng buộc tùy chỉnh.
  * LLM Re-ranking để tinh chỉnh thứ hạng dựa trên mô tả văn bản của nhà (description) so với mong muốn chi tiết của khách hàng.
* [ ] **Tích hợp LLM Explanation**: Tạo báo cáo giải thích chi tiết, tự nhiên bằng tiếng Việt lý do tại sao Top 1 được đề xuất nhiều nhất cho người dùng.
* [ ] **Xây dựng Giao diện Demo (Web App)**:
  * Xây dựng giao diện web (Streamlit hoặc React) để người dùng nhập thông tin và xem kết quả trực quan trên bản đồ.

---

## 🛠️ Công nghệ sử dụng (Tech Stack)
- **Ngôn ngữ chính**: Python 3.x
- **Xử lý dữ liệu**: Pandas, Numpy
- **Địa lý & Bản đồ**: Geopy, Folium, Google Places API / OpenStreetMap
- **AI & LLM**: OpenAI GPT-4o / Gemini 1.5 Pro (LangChain/LlamaIndex)
- **Giao diện**: Streamlit hoặc Next.js
