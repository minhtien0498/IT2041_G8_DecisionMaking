# Hướng dẫn triển khai Solution 2

> Tài liệu thực hành cho **member-2**. Giải thích cách Solution 2 được dựng,
> cách chạy, cách từng module hoạt động, cách mở rộng (cắm LLM/Map API thật),
> và cách nó nối vào phần evaluation của member-4.
>
> Tài liệu liên quan: thiết kế chi tiết ở [Solution-2-Detail.md](Solution-2-Detail.md),
> spec ở [superpowers/specs/2026-06-28-solution2-design.md](superpowers/specs/2026-06-28-solution2-design.md).

---

## 1. Solution 2 là gì

Một pipeline **lai (hybrid)**: giữ form cố định của Solution 1 làm khung tiêu chí
ổn định, rồi dùng một lớp xử lý ngôn ngữ tự nhiên để mở rộng thêm các nhu cầu
free-text mà rule-based chưa có.

```
Form + Additional User Request
  -> Requirement Parsing  (hard / soft / unsupported, dedup với form, map amenity)
  -> Rule-based Top 10    (lọc cứng + chấm điểm form)
  -> Tool Enrichment      (Top 10, mock Search Map API)
  -> Post-filter -> Re-score/Re-rank  (final = α·base + β·additional)
  -> Top 5
  -> Explanation          (giải thích tiếng Việt)
  -> Output contract chung
```

**Nguyên tắc thiết kế:**
- **Deterministic offline**: không cần API key, chạy được mọi lúc, kết quả tái lập
  → lý tưởng cho validation. Mọi thành phần có interface để cắm LLM/Map API thật sau.
- **Tự chứa 100%**: package `src/solution2/` không import gì từ hướng rule-based cũ
  đã bị loại. Tránh phụ thuộc chéo giữa 2 solution final.
- **Toán nền đồng nhất**: công thức min-max normalize và base scoring cho kết quả
  giống Solution 1 trên cùng input form → member-4 so sánh công bằng.

---

## 2. Chạy nhanh (Quickstart)

```bash
# (tùy chọn) tạo venv để chạy test
python3 -m venv .venv
.venv/bin/pip install pytest

# Chạy pipeline trên 12 validation case có free-text
python3 src/demo/run_solution2.py
# -> in tóm tắt từng case + ghi outputs/solution2_results.json

# Chạy test
.venv/bin/python -m pytest tests/ -q     # 25 test
```

**Input:** `data/go_vap_enriched.json` (37 BĐS Gò Vấp đã enrich POI) +
`data/validation_solution2.json` (12 case).
**Output:** `outputs/solution2_results.json` (list object theo output contract chung).

---

## 3. Cấu trúc package `src/solution2/`

| Module | Vai trò | Hàm chính |
|---|---|---|
| `core.py` | Hàm thuần dùng chung | `haversine_m`, `normalize_score` |
| `requirement_parser.py` | Parse free-text → hard/soft/unsupported + dedup | `parse(form, free_text)` |
| `amenity_tools.py` | Mock "Search Map API" trên DB tiện ích cục bộ | `search_amenities`, `geocode`, `known_amenities` |
| `enrichment.py` | Sinh thuộc tính động cho Top 10 | `enrich_top10(top10, parsed)` |
| `scoring.py` | Lọc cứng, base score, additional score, post-filter | `filter_hard`, `score_base`, `score_additional`, `combine`, `post_filter` |
| `explanation.py` | Sinh giải thích tiếng Việt theo template | `explain(top5, parsed, form)` |
| `pipeline.py` | Điều phối toàn bộ flow | `run(form, free_text, properties)` |
| `output_contract.py` | Map kết quả nội bộ → schema chung | `to_contract(case_id, internal, latency_ms)` |

Mỗi module một nhiệm vụ, test được độc lập.

---

## 4. Pipeline ánh xạ vào code (theo từng bước trong design)

### Bước 1–2: Hybrid input + Requirement Parsing
`requirement_parser.parse(form, free_text)` tách free-text thành các mệnh đề rồi
phân loại:

- **soft / hard**: nhu cầu đo lường được. `hard` khi có từ khóa bắt buộc
  ("phải", "tối thiểu", "trong vòng X"); còn lại là `soft`.
- **unsupported**: nhu cầu chủ quan ("yên tĩnh", "phong thủy"…) hoặc không map
  được sang amenity tool hiểu.
- **duplicates**: nhu cầu đã có trong form (vd "gần siêu thị") → hợp nhất, không
  tạo thuộc tính trùng.

**Capability-aware**: chỉ giữ nhu cầu quy đổi được sang `amenity_name` có trong
`AMENITY_DATABASE`. Quy đổi qua **lexicon** (`AMENITY_LEXICON`):

| Cụm từ free-text | amenity_name | Thuộc tính sinh ra |
|---|---|---|
| "nhiều chợ xung quanh" | `market` | `nearby_market_count_within_1000m` (count, higher_better) |
| "gần trường mầm non" | `kindergarten` | `distance_to_nearest_kindergarten_m` (nearest, lower_better) |
| "nhiều quán cà phê" | `cafe` | `nearby_cafe_count_within_1000m` |

Quy tắc count vs distance: có từ "nhiều/càng nhiều/xung quanh/mật độ" → **đếm**
(higher_better); còn "gần/cách" → **khoảng cách gần nhất** (lower_better). Bán
kính lấy từ "X m" / "X km" trong câu, mặc định 1000m.

### Bước 3: Rule-based Top 10
`scoring.filter_hard` lọc theo `budget_max_million` + `min_bedrooms`;
`scoring.score_base` chấm điểm form (giống Solution 1) → sắp xếp → lấy **Top 10**
làm vùng đệm.

### Bước 4: Tool Enrichment cho Top 10
`enrichment.enrich_top10` với MỖI BĐS gọi `amenity_tools.search_amenities` để sinh
**cùng** tập thuộc tính động. Bất biến: thuộc tính tạo cho 1 ứng viên thì tạo cho
toàn bộ Top 10 (để scoring đồng nhất).

### Bước 5: Post-filter + Re-score + Re-rank
- `scoring.post_filter`: loại ứng viên vi phạm hard requirement mới (vd "phải có
  chợ trong 1km" mà count = 0).
- `scoring.score_additional`: chuẩn hóa thuộc tính động min-max **trong nội bộ
  Top 10**, nhân trọng số → `additional_score`.
- `scoring.combine`: `final_score = α·base + β·additional` (mặc định α=0.7, β=0.3).
  Nếu không có soft req đo được → α=1, β=0 (suy biến về Solution 1).

### Bước 6: Top 5 + Explanation
`explanation.explain` sinh giải thích: vì sao thứ hạng đổi sau free-text, BĐS nào
hợp nhu cầu bổ sung nhất, liệt kê nhu cầu unsupported. LLM ở bước này **không**
tự thêm tiêu chí hay đổi thứ hạng.

---

## 5. Output contract chung

`output_contract.to_contract` trả object đúng schema member-4 cần:

```json
{
  "case_id": "S2_001",
  "solution_id": "solution_2",
  "status": "ok",
  "top5": [
    {
      "rank": 1,
      "property_id": "GV_008",
      "total_score": 0.759,
      "hard_constraint_pass": true,
      "reason_tags": ["near_school", "good_market"],
      "base_score": 0.656,
      "additional_score": 1.0,
      "dynamic_attributes": { "nearby_market_count_within_1000m": { "...": "..." } }
    }
  ],
  "explanation_summary": "Top 1 là GV_008 ...",
  "unsupported_requirements": [],
  "latency_ms": 12.3
}
```

**Field bắt buộc** (đúng chuẩn nhóm): `case_id`, `solution_id`, `status`, `top5`,
`top5[].{rank, property_id, total_score, hard_constraint_pass}`,
`explanation_summary`, `unsupported_requirements`, `latency_ms`.
**Field mở rộng** (riêng Solution 2, cho phép thêm): `base_score`,
`additional_score`, `dynamic_attributes`, `reason_tags`.

---

## 6. Validation set Solution 2

`data/validation_solution2.json` — 12 case, mỗi case có `input.user_need_text`,
phủ 4 nhóm bắt buộc:

| Nhóm | case_id | Mục đích |
|---|---|---|
| `clear` | S2_001–003 | Nhu cầu rõ ràng (gồm 1 case free-text rỗng → chạy như Solution 1) |
| `ambiguous_free_text` | S2_004–006 | Mơ hồ, có hard constraint, có duplicate với form |
| `conflict_tradeoff` | S2_007–009 | Vừa đo được vừa chủ quan (tradeoff) |
| `unsupported` | S2_010–012 | Nhu cầu không đo được → phải gắn cờ |

> Lưu ý: `validation_50_scenarios.json` (của member-4) chỉ có form, không có
> free-text. File này là bộ test **riêng** của Solution 2 để chứng minh giá trị
> của phần free-text. Pipeline vẫn chạy được trên cả hai (case không free-text
> suy biến về Solution 1).

---

## 7. Cách mở rộng

### 7.1. Thêm loại tiện ích mới
1. Thêm tọa độ vào `AMENITY_DATABASE` trong `amenity_tools.py`.
2. Thêm cụm từ nhận diện vào `AMENITY_LEXICON` trong `requirement_parser.py`.
Ví dụ thêm "nhà thờ" → `church`: thêm key `church` (list tọa độ) + dòng
`"church": ["nhà thờ"]`.

### 7.2. Cắm LLM thật (thay parser keyword)
Giữ nguyên chữ ký `parse(form, free_text) -> ParsedRequirements`. Trong thân hàm,
gọi LLM với prompt yêu cầu trả JSON đúng cấu trúc `soft/hard/unsupported/duplicates`,
rồi dựng lại `ParsedRequirements`. **Capability-aware vẫn bắt buộc**: chỉ giữ
amenity nằm trong `known_amenities()`. Phần còn lại của pipeline không đổi.

### 7.3. Cắm Map API thật (thay mock)
Thay thân hàm `amenity_tools.search_amenities(lat, lon, amenity_name, radius_m)`
bằng lệnh gọi OSM Overpass / Google Places, trả về đúng
`{"count": int, "nearest_distance_m": float|None}`. Chữ ký không đổi nên enrichment
và scoring giữ nguyên.

### 7.4. Chỉnh trọng số α/β
`pipeline.run(form, free_text, properties, alpha=0.7, beta=0.3)`. Tăng β nếu muốn
nhu cầu free-text ảnh hưởng mạnh hơn lên thứ hạng.

---

## 8. Kiểm thử

`tests/` (pytest), 25 test:

| File | Kiểm tra |
|---|---|
| `test_requirement_parser.py` | Map từ khóa, count vs distance, hard/soft, dedup, unsupported, ưu tiên amenity |
| `test_amenity_tools.py` | Đếm theo bán kính, nearest distance, amenity lạ trả 0 |
| `test_scoring.py` | normalize biên, combine α/β, filter_hard, additional, post_filter |
| `test_pipeline_contract.py` | End-to-end khớp schema, total_score giảm dần, free-text đổi thứ hạng, unsupported, suy biến khi rỗng |

---

## 9. Tiêu chí hoàn thành (Definition of Done)

1. `python3 src/demo/run_solution2.py` chạy không lỗi, sinh output đúng contract. ✅
2. Toàn bộ pytest pass. ✅
3. Case "nhiều chợ xung quanh" làm đổi thứ hạng so với chỉ-form. ✅
4. Case unsupported được gắn cờ đúng trong `unsupported_requirements`. ✅

---

## 10. Bàn giao cho member-4

`outputs/solution2_results.json` đã đúng output contract chung. Member-4 chỉ cần
đọc list này, ghép cùng output của `Solution 1` mới để dựng bảng so sánh
(`solution_1_top5` vs `solution_2_top5`, constraint satisfaction, review comment).
Không cần đổi tên field giữa hai solution.
