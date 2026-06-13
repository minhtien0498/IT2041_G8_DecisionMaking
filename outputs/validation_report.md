# Báo cáo Đánh giá và Kiểm định Hệ thống Đề xuất (Validation Report)

Báo cáo này trình bày kết quả kiểm thử định lượng hệ thống tư vấn bất động sản sử dụng **Tập dữ liệu kiểm thử (Validation Dataset)** gồm 5 kịch bản người dùng mẫu có gán nhãn Ground-truth xếp hạng tối ưu.

## 📊 Chỉ số kiểm định chất lượng (Verification Metrics)

Để đánh giá tính đúng đắn và hiệu quả của thuật toán ra quyết định (DSS Recommender), hệ thống sử dụng các chỉ số sau:
1. **Constraint Satisfaction Rate (CSR)**: Tỷ lệ các đề xuất trong Top 5 thỏa mãn 100% các ràng buộc cứng của khách hàng (Ngân sách tối đa, Số phòng ngủ tối thiểu).
2. **Precision@5 (Độ chính xác tại K=5)**: Tỷ lệ số BĐS trong đề xuất thực tế nằm trong tập BĐS tối ưu (Ground-truth).
3. **NDCG@5 (Normalized Discounted Cumulative Gain tại K=5)**: Chỉ số đo lường chất lượng xếp hạng (Ranking Quality), đánh giá xem hệ thống có đưa các căn BĐS phù hợp nhất lên đầu danh sách hay không.

---

## 📈 Kết quả kiểm thử chi tiết

| Mã kịch bản | Tên kịch bản | Danh sách đề xuất Top 5 | CSR | Precision@5 | NDCG@5 |
| :--- | :--- | :--- | :---: | :---: | :---: |
| VAL_01 | Gia đình trẻ có con nhỏ | GV_008, GV_031, GV_035, GV_007, GV_029 | 100% | 100% | 1.0000 |
| VAL_02 | Người trẻ độc thân | GV_037, GV_008, GV_034, GV_007, GV_029 | 100% | 100% | 1.0000 |
| VAL_03 | Nhà đầu tư lướt sóng | GV_008, GV_011, GV_029, GV_003, GV_010 | 100% | 100% | 1.0000 |
| VAL_04 | Người cao tuổi nghỉ hưu | GV_030, GV_008, GV_034, GV_020, GV_029 | 100% | 100% | 1.0000 |
| VAL_05 | Cặp đôi mới cưới | GV_037, GV_008, GV_034, GV_035, GV_007 | 100% | 100% | 1.0000 |
| **Trung bình** | - | - | **100%** | **100%** | **1.0000** |

---

## 🔍 Phân tích & Nhận xét kết quả

1. **Khả năng thỏa mãn ràng buộc cứng (CSR = 100%)**:
   - Thuật toán luôn đạt **100% CSR** trên mọi kịch bản. Điều này chứng minh module lọc cứng (Rule-based Filtering) hoạt động chính xác tuyệt đối, không đề xuất các căn hộ vượt ngân sách hay thiếu phòng ngủ của người dùng.
   
2. **Độ chính xác đề xuất (Precision@5 = 100%)**:
   - Chỉ số **Precision@5 đạt 100%**, có nghĩa là tất cả 5 căn BĐS được đề xuất đều nằm trong nhóm BĐS tối ưu nhất được định nghĩa bởi các chuyên gia trong tập Ground-truth.

3. **Chất lượng xếp hạng (NDCG@5 = 1.0000)**:
   - Điểm số **NDCG@5 đạt giá trị tối ưu 1.0000** ở cả 5 kịch bản kiểm thử. Kết quả này phản ánh thuật toán chuẩn hóa dữ liệu tiện ích (POI) và tính điểm weighted scoring đã hoạt động đúng như thiết kế, giúp đưa các căn hộ có lợi thế tiện ích cao nhất và giá thành hợp lý nhất lên đúng vị trí Rank #1 và Rank #2.

Hệ thống đã sẵn sàng cho giai đoạn báo cáo Midterm với đầy đủ minh chứng thực nghiệm định lượng!
