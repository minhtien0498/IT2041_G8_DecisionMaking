# 📋 Báo cáo Validation Hệ thống Tư vấn BĐS (50 Scenarios)

**Tổng số kịch bản kiểm thử:** 50
**Phân bổ:** 5 archetype × 10 biến thể mỗi archetype
**Tập dữ liệu:** 37 BĐS tại Quận Gò Vấp, TP.HCM

## 📊 Tổng hợp chỉ số đánh giá (Global Metrics)

| Chỉ số | Giá trị |
| :--- | :---: |
| Constraint Satisfaction Rate (CSR) | **100.0%** |
| Precision@3 | **82.0%** |
| Precision@5 | **76.8%** |
| Recall@3 | **64.3%** |
| Recall@5 | **92.0%** |
| NDCG@3 | **0.9200** |
| NDCG@5 | **0.9200** |
| Mean Average Precision (MAP) | **0.9200** |

---

## 🎯 Phân tích theo nhóm người dùng (Per-Archetype Breakdown)

| Archetype | #Scenarios | Avg CSR | Avg P@5 | Avg R@5 | Avg NDCG@5 | Avg MAP |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 👨‍👩‍👧‍👦 Gia đình | 10 | 100% | 80% | 100% | 1.0000 | 1.0000 |
| 👤 Người trẻ | 10 | 100% | 68% | 100% | 1.0000 | 1.0000 |
| 💰 Nhà đầu tư | 10 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| 🧓 Người cao tuổi | 10 | 100% | 88% | 100% | 1.0000 | 1.0000 |
| 💑 Cặp đôi | 10 | 100% | 48% | 60% | 0.6000 | 0.6000 |

---

## ⚠️ Phân tích Edge Cases

- **Scenarios không có BĐS phù hợp (0 candidates):** 4
  - `VAL_041` — Cặp đôi – mới cưới
  - `VAL_043` — Cặp đôi – DINK (2 thu nhập)
  - `VAL_044` — Cặp đôi – ngân sách hạn chế
  - `VAL_048` — Cặp đôi – cần diện tích lớn
- **Scenarios có ít hơn 5 candidates:** 12
  - `VAL_005` — Gia đình – thu nhập khá (2 candidates)
  - `VAL_007` — Gia đình – ưu tiên công viên (2 candidates)
  - `VAL_008` — Gia đình – ưu tiên siêu thị (2 candidates)
  - `VAL_009` — Gia đình – cần diện tích lớn (4 candidates)
  - `VAL_014` — Người trẻ – thu nhập 15-20tr (1 candidates)
  - `VAL_015` — Người trẻ – thu nhập 25-35tr (1 candidates)
  - `VAL_016` — Người trẻ – cần gần đường lớn (1 candidates)
  - `VAL_017` — Người trẻ – thích khu yên tĩnh (1 candidates)
  - `VAL_036` — Người cao tuổi – cần yên tĩnh (1 candidates)
  - `VAL_038` — Người cao tuổi – muốn nhà rộng (3 candidates)
  - `VAL_042` — Cặp đôi – sắp có con (1 candidates)
  - `VAL_046` — Cặp đôi – gần chợ/siêu thị (3 candidates)

---

## 📈 Kết quả chi tiết từng kịch bản

| ID | Tên kịch bản | #Cands | Top 5 đề xuất | CSR | P@5 | R@5 | NDCG@5 | AP |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| VAL_001 | Gia đình – trẻ có 1 con | 10 | GV_008, GV_035, GV_029, GV_031, GV_007 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_002 | Gia đình – trẻ có 2 con | 14 | GV_035, GV_008, GV_031, GV_007, GV_029 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_003 | Gia đình – đông con (4 người) | 10 | GV_031, GV_008, GV_007, GV_035, GV_029 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_004 | Gia đình – thu nhập trung bình | 14 | GV_008, GV_035, GV_031, GV_007, GV_029 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_005 | Gia đình – thu nhập khá | 2 | GV_006, GV_015 | 100% | 40% | 100% | 1.0000 | 1.0000 |
| VAL_006 | Gia đình – ưu tiên trường quốc tế | 11 | GV_008, GV_029, GV_007, GV_031, GV_035 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_007 | Gia đình – ưu tiên công viên | 2 | GV_006, GV_015 | 100% | 40% | 100% | 1.0000 | 1.0000 |
| VAL_008 | Gia đình – ưu tiên siêu thị | 2 | GV_006, GV_015 | 100% | 40% | 100% | 1.0000 | 1.0000 |
| VAL_009 | Gia đình – cần diện tích lớn | 4 | GV_031, GV_006, GV_033, GV_015 | 100% | 80% | 100% | 1.0000 | 1.0000 |
| VAL_010 | Gia đình – tiết kiệm ngân sách | 14 | GV_008, GV_029, GV_035, GV_007, GV_031 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_011 | Người trẻ – mới ra trường | 10 | GV_008, GV_037, GV_034, GV_007, GV_031 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_012 | Người trẻ – làm IT quận 1 | 10 | GV_008, GV_029, GV_007, GV_031, GV_035 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_013 | Người trẻ – freelancer | 14 | GV_037, GV_008, GV_034, GV_029, GV_031 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_014 | Người trẻ – thu nhập 15-20tr | 1 | GV_037 | 100% | 20% | 100% | 1.0000 | 1.0000 |
| VAL_015 | Người trẻ – thu nhập 25-35tr | 1 | GV_035 | 100% | 20% | 100% | 1.0000 | 1.0000 |
| VAL_016 | Người trẻ – cần gần đường lớn | 1 | GV_037 | 100% | 20% | 100% | 1.0000 | 1.0000 |
| VAL_017 | Người trẻ – thích khu yên tĩnh | 1 | GV_037 | 100% | 20% | 100% | 1.0000 | 1.0000 |
| VAL_018 | Người trẻ – ưu tiên giá rẻ nhất | 5 | GV_008, GV_007, GV_031, GV_035, GV_027 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_019 | Người trẻ – cần 3 phòng ngủ | 10 | GV_008, GV_037, GV_034, GV_007, GV_031 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_020 | Người trẻ – muốn diện tích rộng | 14 | GV_037, GV_008, GV_034, GV_029, GV_007 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_021 | Nhà đầu tư – lướt sóng ngắn hạn | 25 | GV_012, GV_028, GV_008, GV_011, GV_010 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_022 | Nhà đầu tư – đầu tư dài hạn | 21 | GV_004, GV_003, GV_008, GV_029, GV_033 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_023 | Nhà đầu tư – cho thuê | 28 | GV_008, GV_011, GV_003, GV_029, GV_004 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_024 | Nhà đầu tư – ngân sách vừa | 21 | GV_008, GV_029, GV_037, GV_033, GV_034 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_025 | Nhà đầu tư – ngân sách cao | 21 | GV_008, GV_004, GV_029, GV_037, GV_003 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_026 | Nhà đầu tư – ưu tiên mặt tiền | 20 | GV_008, GV_004, GV_029, GV_033, GV_024 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_027 | Nhà đầu tư – ưu tiên diện tích | 19 | GV_008, GV_029, GV_037, GV_034, GV_033 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_028 | Nhà đầu tư – ưu tiên giá/m² thấp | 31 | GV_008, GV_004, GV_011, GV_010, GV_003 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_029 | Nhà đầu tư – gần siêu thị | 31 | GV_008, GV_011, GV_029, GV_003, GV_004 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_030 | Nhà đầu tư – khu dân cư sầm uất | 19 | GV_008, GV_029, GV_007, GV_034, GV_037 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_031 | Người cao tuổi – sống một mình | 5 | GV_008, GV_031, GV_007, GV_027, GV_035 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_032 | Người cao tuổi – sống cùng vợ/chồng | 19 | GV_030, GV_008, GV_034, GV_020, GV_029 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_033 | Người cao tuổi – cần gần bệnh viện | 14 | GV_008, GV_031, GV_029, GV_036, GV_035 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_034 | Người cao tuổi – ưu tiên công viên tập thể dục | 23 | GV_030, GV_008, GV_034, GV_020, GV_029 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_035 | Người cao tuổi – ngân sách hưu trí | 23 | GV_030, GV_008, GV_034, GV_020, GV_029 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_036 | Người cao tuổi – cần yên tĩnh | 1 | GV_037 | 100% | 20% | 100% | 1.0000 | 1.0000 |
| VAL_037 | Người cao tuổi – gần chợ/siêu thị | 16 | GV_030, GV_008, GV_034, GV_020, GV_029 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_038 | Người cao tuổi – muốn nhà rộng | 3 | GV_030, GV_037, GV_035 | 100% | 60% | 100% | 1.0000 | 1.0000 |
| VAL_039 | Người cao tuổi – ngân sách trung bình | 17 | GV_008, GV_029, GV_036, GV_031, GV_011 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_040 | Người cao tuổi – gần con cháu | 10 | GV_008, GV_029, GV_036, GV_031, GV_035 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_041 | Cặp đôi – mới cưới | 0 | ∅ | 100% | 0% | 0% | 0.0000 | 0.0000 |
| VAL_042 | Cặp đôi – sắp có con | 1 | GV_035 | 100% | 20% | 100% | 1.0000 | 1.0000 |
| VAL_043 | Cặp đôi – DINK (2 thu nhập) | 0 | ∅ | 100% | 0% | 0% | 0.0000 | 0.0000 |
| VAL_044 | Cặp đôi – ngân sách hạn chế | 0 | ∅ | 100% | 0% | 0% | 0.0000 | 0.0000 |
| VAL_045 | Cặp đôi – ngân sách thoải mái | 17 | GV_008, GV_007, GV_029, GV_034, GV_037 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_046 | Cặp đôi – gần chợ/siêu thị | 3 | GV_037, GV_035, GV_030 | 100% | 60% | 100% | 1.0000 | 1.0000 |
| VAL_047 | Cặp đôi – gần trường cho con | 16 | GV_008, GV_037, GV_029, GV_034, GV_007 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_048 | Cặp đôi – cần diện tích lớn | 0 | ∅ | 100% | 0% | 0% | 0.0000 | 0.0000 |
| VAL_049 | Cặp đôi – muốn giá rẻ | 8 | GV_029, GV_008, GV_007, GV_035, GV_031 | 100% | 100% | 100% | 1.0000 | 1.0000 |
| VAL_050 | Cặp đôi – khu an ninh tốt | 10 | GV_008, GV_029, GV_007, GV_031, GV_035 | 100% | 100% | 100% | 1.0000 | 1.0000 |

---

## 🔍 Phân tích & Nhận xét

### 1. Constraint Satisfaction Rate (CSR)
- CSR đạt **100%** trên toàn bộ 50 scenarios → Module lọc cứng (Hard Constraint Filter) hoạt động hoàn hảo.

### 2. Chất lượng đề xuất (Precision & Recall)
- **Precision@5 = 76.8%**: Tỷ lệ BĐS đề xuất trùng với ground-truth.
- **Recall@5 = 92.0%**: Tỷ lệ BĐS ground-truth được tìm thấy trong đề xuất.

### 3. Chất lượng xếp hạng (NDCG & MAP)
- **NDCG@5 = 0.9200**: Đo lường chất lượng thứ tự xếp hạng.
- **MAP = 0.9200**: Mean Average Precision đo lường toàn diện.

### 4. Robustness qua các nhóm người dùng
- Hệ thống được kiểm thử trên **5 archetype khác nhau**, mỗi archetype có 10 biến thể tham số.
- Điều này đảm bảo DSS hoạt động ổn định trên các nhu cầu đa dạng: gia đình, người trẻ, nhà đầu tư, người cao tuổi, cặp đôi.

### 5. Edge Cases
- 4 scenarios không có BĐS nào thỏa mãn ràng buộc cứng → Hệ thống trả về danh sách rỗng (đúng hành vi mong đợi).
- 12 scenarios có ít hơn 5 candidates → Đánh giá khả năng graceful degradation của hệ thống.
