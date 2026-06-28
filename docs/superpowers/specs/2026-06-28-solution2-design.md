# Spec thiết kế: Solution 2 — Pipeline lai Form + Free-text

- **Ngày:** 2026-06-28
- **Người phụ trách:** member-2 (Solution 2)
- **Trạng thái:** Đã duyệt thiết kế, sẵn sàng triển khai

## 1. Mục tiêu

Triển khai Solution 2 theo `docs/Solution-2-Detail.md`: giữ form cố định của Solution 1 làm khung tiêu chí ổn định, dùng một lớp xử lý ngôn ngữ tự nhiên (deterministic, có thể thay bằng LLM thật sau) để mở rộng phạm vi tiêu chí mà hệ thống hiểu và đo lường được, rồi enrichment + re-rank và sinh giải thích.

Pipeline:

```
Form + Additional User Request
  -> Requirement Parsing (hard / soft / unsupported, dedup với form, map amenity)
  -> Rule-based Top 10 (lọc cứng + chấm điểm form)
  -> Tool-based Attribute Enrichment (Top 10, mock Search Map API)
  -> Post-filtering -> Re-scoring/Re-ranking (final = alpha*base + beta*additional)
  -> Top 5
  -> Explanation (template tiếng Việt)
  -> Output theo contract chung
```

## 2. Ràng buộc thiết kế (đã chốt với người dùng)

1. **Backend deterministic offline.** Không gọi LLM/API thật. Parser dùng từ khóa, "Search Map API" là database tiện ích cục bộ, explanation theo template. Mọi thành phần có interface để cắm LLM/Map API thật về sau.
2. **Dataset:** `data/go_vap_enriched.json` (37 BĐS Gò Vấp đã enrich POI). Cùng nguồn với Solution 1 để so sánh công bằng.
3. **Phạm vi:** pipeline chạy được + xuất đúng output contract chung + chạy thử trên validation set. Không gồm report/slide.
4. **Tự chứa 100%.** `src/solution2/` KHÔNG import từ `src/demo/run_pipeline.py` (Solution 1). Tránh phụ thuộc chéo giữa member-1 và member-2.
5. **Đồng nhất toán nền.** Công thức min-max normalize và cách chấm `base_score` cho kết quả giống Solution 1 trên cùng input form, để member-4 so sánh công bằng. Đây là yêu cầu của output contract, không phải reuse code.

## 3. Kiến trúc — package `src/solution2/`

Mỗi module một nhiệm vụ, test được độc lập.

### 3.1. `core.py`
Hàm thuần dùng chung trong nội bộ Solution 2:
- `haversine_m(lat1, lon1, lat2, lon2) -> float`: khoảng cách mét.
- `normalize_score(value, vmin, vmax, direction) -> float`: min-max về `[0,1]`, `direction` ∈ {`lower_better`, `higher_better`}.

### 3.2. `requirement_parser.py`
- Hàm chính: `parse(form: dict, free_text: str) -> ParsedRequirements`.
- `ParsedRequirements` gồm: `soft` (list), `hard` (list), `unsupported` (list các chuỗi mô tả).
- Mỗi requirement đo lường được có: `raw_phrase`, `amenity_name`, `derived_attribute`, `radius_m`, `direction`, `weight`, `agg` (`count` | `nearest_distance`), `duplicate_of` (tên field form nếu trùng, ngược lại `None`).
- **Lexicon** map cụm từ tiếng Việt -> `amenity_name`, ví dụ: chợ→`market`, mầm non/mẫu giáo→`kindergarten`, cà phê/cafe→`cafe`, nhà thuốc→`pharmacy`, gym/phòng tập→`gym`, trường→`school`, bệnh viện→`hospital`, siêu thị→`supermarket`, công viên→`park`.
- **Capability-aware:** chỉ giữ nhu cầu map được sang `amenity_name` có trong `AMENITY_DATABASE`. Nhu cầu chủ quan (yên tĩnh, vibe tốt, hàng xóm thân thiện) -> `unsupported`.
- **Phân loại hard/soft:** có từ khóa bắt buộc ("phải", "bắt buộc", "tối thiểu", "trong vòng X m") -> `hard`; còn lại ("ưu tiên", "càng nhiều càng tốt", "gần") -> `soft`.
- **Dedup với form:** nếu amenity đã có trong form (school, park, supermarket, boulevard) thì gắn `duplicate_of` và KHÔNG tạo thuộc tính động trùng; thay vào đó có thể nâng nhẹ weight của tiêu chí form tương ứng (merge), không tạo cột mới.
- Interface ổn định để thay bằng LLM thật (cùng chữ ký, cùng kiểu trả về).

### 3.3. `amenity_tools.py`
- `AMENITY_DATABASE`: dict `amenity_name -> [{name, lat, lon}]`, tọa độ thực tế quanh Gò Vấp cho ~8 loại tiện ích (market, cafe, kindergarten, pharmacy, gym, school, hospital, supermarket, park, boulevard).
- `search_amenities(lat, lon, amenity_name, radius_m) -> {"count": int, "nearest_distance_m": float|None}`. Cùng chữ ký một lệnh gọi OSM/Overpass thật, để swap dễ dàng.
- `geocode(prop) -> (lat, lon)`: lấy từ field `latitude`/`longitude` có sẵn (mock tool "lat,long từ địa chỉ").

### 3.4. `enrichment.py`
- `enrich_top10(top10: list, parsed: ParsedRequirements) -> list`: với MỖI BĐS sinh CÙNG tập thuộc tính động từ các req đo lường được:
  - `agg=count` -> `nearby_<amenity>_count_within_<radius>m` (higher_better).
  - `agg=nearest_distance` -> `distance_to_nearest_<amenity>_m` (lower_better).
- Bất biến: nếu một thuộc tính động được tạo cho 1 ứng viên thì tạo cho TOÀN BỘ Top 10.

### 3.5. `scoring.py`
- `filter_hard(properties, form) -> (candidates, rejected)`: lọc theo `budget_max_million`, `min_bedrooms`.
- `score_base(candidates, form) -> list`: chấm điểm form (giống công thức Solution 1), trả `base_score` + breakdown.
- `score_additional(enriched, parsed) -> list`: chuẩn hóa thuộc tính động về `[0,1]` theo min-max trong nội bộ Top 10, nhân weight, ra `additional_score` + `dynamic_attributes`.
- `combine(base, additional, alpha=0.7, beta=0.3) -> final_score`.
- `post_filter(enriched, parsed)`: loại ứng viên vi phạm hard constraint mới (nếu đo được sau enrichment).

### 3.6. `explanation.py`
- `explain(top5, parsed, form) -> str`: template tiếng Việt — vì sao thứ hạng đổi sau free-text, BĐS nào hợp nhu cầu bổ sung nhất, điểm mạnh/yếu, liệt kê `unsupported`. Không tự thêm tiêu chí/đổi thứ hạng. Pluggable cho LLM thật.

### 3.7. `pipeline.py`
- `run(form, free_text, properties, *, alpha=0.7, beta=0.3) -> InternalResult`: điều phối toàn bộ flow. Suy biến mềm: `free_text` rỗng -> bỏ enrichment, `beta=0`, hành xử như Solution 1.

### 3.8. `output_contract.py`
- `to_contract(case_id, internal_result, latency_ms) -> dict` theo schema chung:
  - Bắt buộc: `case_id`, `solution_id="solution_2"`, `status`, `top5[].{rank, property_id, total_score, hard_constraint_pass, reason_tags}`, `explanation_summary`, `unsupported_requirements`, `latency_ms`.
  - Mở rộng (cho phép): `top5[].{base_score, additional_score, dynamic_attributes}`.

## 4. Entry point — `src/demo/run_solution2.py`
CLI: load `data/go_vap_enriched.json` + `data/validation_solution2.json` -> chạy pipeline từng case -> in tóm tắt + ghi `outputs/solution2_results.json` (list các object theo contract).

## 5. Dữ liệu test — `data/validation_solution2.json`
~12 case trên 37 BĐS, mỗi case có `case_id`, `persona`, `input.{budget_max_million, min_bedrooms, ...form..., user_need_text}`, `expected.{hard_constraints, soft_priorities, unsupported_requirements}`, `case_group`. Phủ 4 nhóm:
- rõ ràng (clear),
- free-text mơ hồ (ambiguous),
- mâu thuẫn/tradeoff,
- unsupported / đo lường khó.

## 6. Kiểm thử — `tests/`
pytest:
- `test_requirement_parser.py`: map từ khóa đúng amenity; dedup-với-form gắn `duplicate_of`; nhu cầu chủ quan -> `unsupported`; phân loại hard/soft.
- `test_amenity_tools.py`: đếm theo bán kính đúng; `nearest_distance_m` đúng; amenity không tồn tại trả count 0.
- `test_scoring.py`: `normalize_score` biên; `final = alpha*base + beta*additional`; post-filter loại đúng ứng viên.
- `test_pipeline_contract.py`: end-to-end 1 case -> output có đủ field bắt buộc của contract, `top5` đúng tối đa 5 dòng, `rank` tăng dần.

## 7. Tiêu chí hoàn thành (Definition of Done)
1. `python3 src/demo/run_solution2.py` chạy không lỗi, sinh `outputs/solution2_results.json` đúng contract.
2. Tất cả test pytest pass.
3. Case free-text "nhiều chợ xung quanh" làm thay đổi thứ hạng so với chỉ-form (chứng minh giá trị Solution 2).
4. Case unsupported được gắn cờ đúng trong `unsupported_requirements`.

## 8. Ngoài phạm vi
LLM/API thật; dataset 100 BĐS; report/slide; tích hợp web UI.
