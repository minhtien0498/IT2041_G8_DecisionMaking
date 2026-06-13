# Hướng dẫn Mở rộng Dữ liệu & Kiểm định Nhu cầu Nhà ở

Để giải quyết triệt để đánh giá **"Thiếu tập data validation về nhu cầu nhà ở"** và **"Quy mô dữ liệu quá nhỏ (37 mẫu)"**, Nhóm 8 có thể triển khai dự án theo các hướng mở rộng chi tiết dưới đây cho bản báo cáo cuối kỳ (Final Project).

---

## 🧭 Hướng 1: Mở rộng bộ dữ liệu Bất động sản (TP.HCM Scale)

Hiện tại, subset 37 BĐS Gò Vấp chỉ phục vụ chạy thử nghiệm (midterm baseline). Dữ liệu gốc `docs/data_public.csv` có tới **51,304 mẫu** phủ khắp TP.HCM.

### 🔹 Cách thực hiện:
1. **Mở rộng phạm vi địa lý**:
   - Chỉnh sửa `src/data/prepare_data.py` để không chỉ lọc riêng Gò Vấp mà mở rộng ra các quận lân cận (Bình Thạnh, Thủ Đức, Tân Bình, Quận 7...) hoặc **toàn bộ TP.HCM**.
2. **Nâng quy mô mẫu**:
   - Tăng giới hạn trích xuất lên **500 - 1,000 căn hộ/nhà riêng sạch** (đầy đủ tọa độ lat/lon và thông số phòng).
3. **Mã hóa tự động POI**:
   - Sử dụng thư viện Python kết nối API để cào tự động (hoặc tải dữ liệu OpenStreetMap toàn bộ TP.HCM) nhằm tính khoảng cách tiện ích tự động cho hàng ngàn căn hộ, thay vì hardcode danh sách tiện ích tĩnh.

---

## 🎯 Hướng 2: Xây dựng tập dữ liệu Kiểm định Nhu cầu (Customer Preference Validation Set)

Có 3 phương án để nhóm xây dựng một tập Validation về "nhu cầu nhà ở" thực tế và chuyên nghiệp:

### 📌 Phương án A: Khảo sát người dùng thực tế (User Survey Dataset)
Đây là phương án được các thầy cô đánh giá cao nhất vì có dữ liệu thực tế từ thị trường Việt Nam.
1. **Tạo bảng khảo sát (Google Form)**:
   - Thu thập thông tin từ ~50 đến 100 người dùng thực tế tại Việt Nam với các câu hỏi:
     - *Ràng buộc cứng*: Ngân sách tối đa muốn mua, số phòng ngủ tối thiểu, khu vực mong muốn.
     - *Mức độ ưu tiên (Thang điểm 1-5)*: Độ quan trọng của Trường học, Công viên, Bệnh viện, Siêu thị, Giao thông.
     - *Nhu cầu mô tả tự do*: "Tôi cần tìm nhà hẻm yên tĩnh, có chỗ đỗ xe..."
2. **Số hóa thành tập dữ liệu**:
   - Xuất dữ liệu khảo sát từ Google Form ra file CSV: `data/user_survey_preferences.csv`.
   - Viết module đọc file này, tự động chuyển đổi thang điểm 1-5 của người dùng thành các trọng số mềm $[0, 1]$ phục vụ thuật toán scoring.

### 📌 Phương án B: Giả lập tập khách hàng (Monte Carlo Simulation Dataset)
Nếu thời gian khảo sát hạn chế, nhóm có thể viết script giả lập hành vi để tạo ra tập dữ liệu kiểm định lớn.
1. **Thuật toán sinh dữ liệu**:
   - Viết script Python sinh ngẫu nhiên **200 - 500 hồ sơ khách hàng giả lập**.
   - Các tham số ngân sách, số phòng và trọng số tiện ích được phân phối ngẫu nhiên theo phân phối chuẩn (Normal Distribution) dựa trên các nghiên cứu thị trường thực tế (ví dụ: Ngân sách tập trung nhiều ở phân khúc 3 - 7 tỷ).
2. **Mục tiêu**:
   - Dùng tập dữ liệu này để chạy Stress Test kiểm tra hiệu năng tính toán và độ ổn định của thuật toán xếp hạng khi có lượng lớn người truy cập cùng lúc.

### 📌 Phương án C: Sử dụng bộ dữ liệu khảo sát quốc tế (Public Survey Dataset)
Tận dụng các khảo sát hành vi tiêu dùng bất động sản đã có trên thế giới:
1. **Global House Purchase Decision Dataset (Kaggle)**:
   - Chứa 200,000 hồ sơ quyết định mua nhà của khách hàng bao gồm các đánh giá chủ quan về môi trường xung quanh.
2. **American Housing Survey (AHS)**:
   - Cung cấp dữ liệu chi tiết về lý do và sở thích lựa chọn nhà ở của người tiêu dùng.
3. **Ánh xạ (Mapping)**:
   - Viết code ánh xạ các cột dữ liệu khảo sát này về định dạng kịch bản tương thích với hệ thống để chạy validation trên tập BĐS TP.HCM.
