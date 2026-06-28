# Kết quả sơ khởi Solution 1 Pipeline — Midterm 13/6

## Tổng quan

| Thông tin | Giá trị |
|-----------|---------|
| **Pipeline** | Solution 1: Form → Rule-based Filtering → Rule-based Scoring → Top 5 |
| **Dataset** | data_public.csv (HCMC 2025 — Kaggle) |
| **Subset** | 37 BĐS "Nhà riêng" tại Quận Gò Vấp, TP.HCM |
| **Tiêu chí lọc subset** | Có lat/lon, có bedrooms & bathrooms (1-10), giá 500tr-30 tỷ, diện tích 20-500m² |
| **POI enrichment** | Tính khoảng cách Haversine đến 8 trường học, 4 công viên, 3 bệnh viện, 5 siêu thị, 4 trục đường lớn thực tế tại Gò Vấp |
| **Số personas test** | 3 |

---

## Input/Output mẫu

### Input (User Scenario): Gia đình có con nhỏ

```json
{
  "name": "Gia đình có con nhỏ",
  "description": "Gia đình 4 người, có 2 con nhỏ đang học cấp 1. 
                  Ngân sách dưới 8 tỷ, cần ít nhất 3 phòng ngủ.
                  Ưu tiên gần trường học và công viên.",
  "hard_constraints": {
    "budget_max": "8 tỷ",
    "min_bedrooms": 3
  },
  "soft_preferences": {
    "price":                         { "weight": 0.25, "direction": "lower_better" },
    "distance_to_nearest_school_m":  { "weight": 0.25, "direction": "lower_better" },
    "distance_to_nearest_park_m":    { "weight": 0.20, "direction": "lower_better" },
    "distance_to_nearest_supermarket_m": { "weight": 0.15, "direction": "lower_better" },
    "area_m2":                       { "weight": 0.15, "direction": "higher_better" }
  }
}
```

### Output: Top 5 BĐS phù hợp nhất

```json
{
  "rank": 1,
  "property_id": "GV_008",
  "title": "SIÊU PHẨM TRUNG TÂM GÒ VẤP - NHÀ MỚI Ở NGAY",
  "price": "4.55 tỷ",
  "area": "60 m²",
  "bedrooms": 3,
  "total_score": 0.6558,
  "score_breakdown": {
    "price":           "0.690 × 0.25 = 0.1725",
    "gần trường học":  "0.693 × 0.25 = 0.1732",
    "gần công viên":   "0.706 × 0.20 = 0.1412",
    "gần siêu thị":   "0.876 × 0.15 = 0.1314",
    "diện tích":       "0.250 × 0.15 = 0.0375"
  }
}
```

---

## Kết quả chi tiết 3 Scenarios

### Scenario 1: Gia đình có con nhỏ
- **Điều kiện**: Giá ≤ 8 tỷ, ≥ 3 phòng ngủ
- **Kết quả lọc**: 13/37 BĐS qua (24 bị loại)

| Rank | ID | Score | Giá (tỷ) | DT (m²) | PN | Trường | Công viên | Siêu thị |
|------|----|-------|----------|---------|----|--------|-----------|----------|
| **#1** | **GV_008** | **0.6558** | 4.55 | 60 | 3 | 614m | 588m | 186m |
| #2 | GV_031 | 0.6383 | 4.72 | 40 | 4 | 711m | 121m | 372m |
| #3 | GV_035 | 0.6322 | 4.10 | 33 | 3 | 110m | 915m | 613m |
| #4 | GV_007 | 0.6222 | 4.80 | 42.6 | 3 | 772m | 488m | 83m |
| #5 | GV_029 | 0.6053 | 5.28 | 49 | 3 | 197m | 1043m | 255m |

> **Nhận xét**: GV_008 đứng #1 nhờ cân bằng tốt: giá vừa phải (4.55 tỷ), gần trường (614m), gần công viên (588m), rất gần siêu thị (186m). GV_031 đứng #2 nhờ rất gần công viên (121m) nhưng diện tích nhỏ hơn.

---

### Scenario 2: Người trẻ độc thân
- **Điều kiện**: Giá ≤ 5.5 tỷ, ≥ 2 phòng ngủ
- **Kết quả lọc**: 14/37 BĐS qua (23 bị loại)

| Rank | ID | Score | Giá (tỷ) | DT (m²) | PN | Siêu thị | Đường lớn |
|------|----|-------|----------|---------|----|----------|-----------|
| **#1** | **GV_037** | **0.6380** | 2.85 | 26 | 2 | 269m | 472m |
| #2 | GV_008 | 0.5413 | 4.55 | 60 | 3 | 186m | 727m |
| #3 | GV_034 | 0.4967 | 4.55 | 38 | 2 | 149m | 1010m |
| #4 | GV_007 | 0.4551 | 4.80 | 42.6 | 3 | 83m | 1182m |
| #5 | GV_029 | 0.4536 | 5.28 | 49 | 3 | 255m | 393m |

> **Nhận xét**: GV_037 đứng #1 nhờ giá rất rẻ (2.85 tỷ) — với trọng số 0.35 cho giá, đây là lợi thế lớn. Nhưng diện tích chỉ 26m² nên điểm diện tích thấp. Trade-off rõ ràng.

---

### Scenario 3: Nhà đầu tư
- **Điều kiện**: Giá ≤ 15 tỷ, ≥ 1 phòng ngủ
- **Kết quả lọc**: 31/37 BĐS qua (6 bị loại)

| Rank | ID | Score | Giá (tỷ) | DT (m²) | Giá/m² (tr) | Đường lớn | Siêu thị |
|------|----|-------|----------|---------|-------------|-----------|----------|
| **#1** | **GV_008** | **0.5875** | 4.55 | 60 | 75.8 | 727m | 186m |
| #2 | GV_011 | 0.5727 | 10.5 | 88 | 119.3 | 568m | 104m |
| #3 | GV_029 | 0.5399 | 5.28 | 49 | 107.8 | 393m | 255m |
| #4 | GV_003 | 0.5275 | 8.95 | 95 | 94.2 | 1052m | 640m |
| #5 | GV_010 | 0.5261 | 13.5 | 119.1 | 113.4 | 475m | 528m |

> **Nhận xét**: GV_008 lại đứng #1 nhờ giá/m² thấp nhất (75.8 triệu/m²) và rất gần siêu thị. GV_011 đứng #2 với diện tích lớn (88m²) và gần đường lớn (568m) nhưng giá/m² cao hơn.

---

## Phân tích kết quả

### Observations
1. **GV_008 xuất hiện trong Top 5 cả 3 scenarios** — đây là BĐS "tổng hòa" tốt nhất: giá hợp lý (4.55 tỷ), vị trí trung tâm Gò Vấp, gần nhiều tiện ích
2. **Filtering loại bỏ hiệu quả**: Gia đình chỉ còn 13/37, Người trẻ chỉ còn 14/37 → Hard constraints hoạt động đúng
3. **Trọng số ảnh hưởng rõ**: Khi weight cho giá = 0.35 (người trẻ), BĐS rẻ nhất lên #1. Khi weight cho trường = 0.25 (gia đình), BĐS gần trường lên cao hơn
4. **Trade-off được thể hiện**: GV_037 giá rẻ nhất nhưng diện tích nhỏ nhất — scoring cho thấy rõ đánh đổi

### Validation sơ bộ
| Metric | Kết quả |
|--------|---------|
| **Constraint satisfaction** | ✅ 100% — không có BĐS nào trong Top 5 vi phạm budget hoặc min bedrooms |
| **Score transparency** | ✅ Mỗi recommendation có breakdown điểm chi tiết |
| **Ranking stability** | ✅ Cùng input → cùng output (deterministic, rule-based) |
| **Persona relevance** | ✅ Top 5 khác nhau rõ ràng giữa 3 personas |

---

## Pipeline đã chạy

```
data_public.csv (51,304 listings)
    │
    ▼ Lọc: Nhà riêng + lat/lon + bedrooms + bathrooms sạch
37 BĐS tại Gò Vấp
    │
    ▼ Enrichment: Haversine distance → 8 trường, 4 CV, 3 BV, 5 ST, 4 đường lớn
37 BĐS enriched
    │
    ▼ User Input (3 personas)
    │
    ▼ Rule-based Filtering (hard constraints)
    │
    ▼ Rule-based Scoring (normalized [0,1] × weight)
    │
    ▼ Ranking → Top 5
    │
    ▼ Output: Score breakdown + recommendation
```

---

## Limitations & Next Steps

| Hạn chế | Hướng khắc phục |
|---------|-----------------|
| POI dùng tọa độ ước lượng (chưa gọi API thật) | Dùng Google Places API hoặc OpenStreetMap để lấy POI chính xác |
| Chỉ test trên 1 quận (Gò Vấp) | Mở rộng ra 2-3 quận cho bản final |
| Chưa có LLM explanation | Bổ sung ở Solution 2 Pipeline |
| Trọng số do nhóm tự thiết kế | Có thể cho user tự chọn qua form hoặc dùng persona-based defaults |
| Chỉ có 37 BĐS | Bản final sẽ dùng 200-500 listings |
