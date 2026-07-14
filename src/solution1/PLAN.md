# Plan: Solution 1 — Sequential 2-LLM Pipeline (thay bản ReAct-agent-tự-trị cũ)

> **Bản này thay thế thiết kế "LLM Agent tự trị" trước đó** (ReAct loop với điều kiện dừng
> "diversity ≥ 2 góc nhìn", `vector_search`). Ý tưởng gốc vẫn tham khảo từ
> [docs/source_notes/Solution-1-Detail.md](../../docs/source_notes/Solution-1-Detail.md) (LLM +
> tool-use) nhưng được **thu hẹp lại thành 1 luồng tuần tự có giới hạn rõ ràng, không phải autonomous agent** — theo yêu cầu redesign của user.
> Input/output CONTRACT giữ nguyên. Solution 2 giữ nguyên, không đổi.

## Bối cảnh / ràng buộc tương thích

Phải tương thích với:
- [docs/output_contract_shared.md](../../docs/output_contract_shared.md) — schema output dùng
  chung. [src/solution2/output_contract.py](../solution2/output_contract.py) là bản tham chiếu để
  mirror (`SOLUTION_ID = "solution_1"`).
- [data/validation_cases_v1.json](../../data/validation_cases_v1.json) — validation set chính
  thức của member-4. Form dùng `budget_max_million`, `min_bedrooms`,
  `soft_preferences{weight,direction,min,max}`, `user_need_text`.
- [data/go_vap_tan_binh_100_enriched.json](../../data/go_vap_tan_binh_100_enriched.json) — dataset
  100 căn đã enrich của member-3 (`property_id` dạng `GV_001`/`TB_...`, có sẵn
  `distance_to_nearest_{school,park,hospital,supermarket,boulevard}_m` tính bằng Haversine, cùng
  `nearest_*_name`, `near_*_count_1km`).

Convention của repo (theo
[docs/solution2_implementation_guide.md](../../docs/solution2_implementation_guide.md)): mỗi
solution là 1 package tự chứa (`src/solution1/` hay `src/solution2/`), **không cross-import** giữa
2 solution. Các hàm toán dùng chung (`haversine_m`) được nhân bản riêng ở mỗi package.

**Bỏ qua test suite/unit test chính thức trong giai đoạn build này** (quyết định mới của user):
không viết `MockLLMClient`/mock HTTP Mapbox, không cần Postgres test riêng biệt. User sẽ cung cấp
`OPENROUTER_API_KEY` + `MAPBOX_TOKEN` thật ngay từ đầu để **test trực tiếp bằng cách chạy pipeline
thật** trong lúc develop (không phải viết `pytest`). Mục tiêu ưu tiên: build được pipeline chạy
end-to-end, không phải coverage test. (Có thể bổ sung test sau nếu cần, nhưng không nằm trong
scope hiện tại.)

**Fairness constraint (quan trọng, note của user)**: để so sánh công bằng giữa các solution và dễ
đánh giá trên tập test, Solution 1 phải **luôn trả về BĐS nằm trong tập dataset JSON** — không bao
giờ để LLM tự "bịa" ra property. Đây là lý do có bước **guardrail grounding** bắt buộc bên dưới.

## Flow mới (tuần tự, KHÔNG phải autonomous agent)

```
form + free_text
  -> LLM #1 "Reasoner" (bounded tool-calling, cap cứng 3 turns)
       turn 1 (bắt buộc): sql_filter(conditions) — hard filter từ CÁC FIELD CÓ TRONG FORM
       turn 2..3 (tùy chọn): fetch_nearby_custom / get_distance_to_place khi dữ liệu có sẵn
                              không đủ so với nhu cầu (xem "Khi nào cần enrichment" bên dưới)
       turn cuối (bị ép nếu hết budget, tool_choice="none"): xuất JSON candidates
                              {property_id, total_score, hard_constraint_pass, reason_tags,
                               why_recommended, tradeoff} — LLM TỰ CHẤM total_score
  -> Guardrail/repair (code thuần, KHÔNG LLM):
       - lọc bỏ property_id không thuộc candidate set trả về từ sql_filter (chống hallucination)
       - dedupe, sort desc theo total_score, renumber rank 1..N, cắt top_k=5
  -> LLM #2 "Explainer" (single-shot, KHÔNG có tool access)
       input: form + free_text + top5 đã guard + trace của LLM #1
       output: explanation_summary (+ có thể làm giàu why_recommended/tradeoff mỗi item)
  -> output_contract.to_contract() -> outputs/solution1_results.json
```

Nếu `sql_filter` trả về rỗng → short-circuit `status="no_candidate"`, **không gọi LLM nào** (tiết
kiệm quota, và tránh trường hợp LLM tự bịa candidate khi không có gì để chọn).

## Quyết định đã chốt (qua các vòng hỏi-đáp với user)

1. **Scoring**: LLM #1 tự chấm `total_score`/xếp hạng (KHÔNG dùng công thức weighted min-max
   deterministic như Solution 2 — đây là điểm khác biệt cố ý so với Solution 2). Code chỉ làm
   guardrail: re-sort theo `total_score` desc + renumber rank + validate grounding — không tự
   tính lại điểm.
2. **Flow style LLM #1**: multi-turn native tool-calling, cap cứng **3 turns**. Turn đầu bắt buộc
   là `sql_filter`. Nếu hết budget mà model vẫn muốn gọi tool → ép turn cuối bằng
   `tool_choice="none"` để buộc xuất JSON thay vì tiếp tục gọi tool.
3. **Khi nào cần enrichment** (dataset đã có sẵn 5 cột `distance_to_nearest_{school,park,
   hospital,supermarket,boulevard}_m` + `near_*_count_1km`):
   - free_text nhắc **địa điểm cụ thể** không phải "gần nhất theo loại" (vd "gần chỗ làm ở địa chỉ
     X", "gần chợ Y cụ thể", "gần trường Z cụ thể" — khác với "gần trường học" chung chung).
   - user muốn tiện ích nằm trong **bán kính tùy chỉnh** khác mặc định (vd "trường + bệnh viện
     trong bán kính 300m" thay vì cột có sẵn/1km mặc định).
   → Thiết kế 2 tool enrichment **batched theo danh sách candidate** (không phải per-property/lượt)
   để tiết kiệm turn budget:
   - `get_distance_to_place(candidate_ids, place_query_or_address)` — geocode 1 lần (Mapbox
     Geocoding API), rồi haversine tới từng candidate, trả list `{property_id, distance_m}`.
   - `fetch_nearby_custom(candidate_ids, amenity, radius_m)` — Mapbox Tilequery quanh từng
     candidate với radius tùy chỉnh, trả `{property_id, count, nearest_m}`.
   - **KHÔNG dùng `vector_search`** (bỏ hẳn khỏi scope — đúng tinh thần "không dùng AI agent
     framework, chỉ là 1 ReAct LLM tuần tự").
4. **LLM #2 dùng chung `OpenRouterLLMClient`/rotation pool** với LLM #1, chỉ khác system prompt.
   Vì pool có thể hết hạn/rate-limit, **mỗi stage có model mặc định riêng** nhưng cùng rotation
   pool để fallback lẫn nhau:
   - `SOLUTION1_LLM_MODEL_REASONING` (mặc định `openai/gpt-oss-20b:free`)
   - `SOLUTION1_LLM_MODEL_EXPLANATION` (mặc định có thể khác, vd `qwen/qwen3-coder:free`)
   - `SOLUTION1_LLM_MODEL_POOL` vẫn là danh sách fallback dùng chung cho cả 2 stage (phân tách
     bằng dấu phẩy). Model pool tham khảo: `openai/gpt-oss-20b:free`, `qwen/qwen3-coder:free`,
     `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3-ultra-550b-a55b:free`,
     `openai/gpt-oss-120b:free` (fallback mạnh hơn). Không dùng `gpt-4o-mini` (trả phí, không
     free).
   - `OpenRouterLLMClient` thử model mặc định của stage, tự fallback sang model kế tiếp trong pool
     khi lỗi/429, và **ghi lại model nào đã phục vụ mỗi lần gọi** (trong trace) để so sánh hiệu
     quả sau.
5. **Phạm vi hard filter của `sql_filter`**: áp dụng cho **mọi field định lượng có trong form**
   (hiện tại: `budget_max_million` → `price_million_vnd <= X`, `min_bedrooms` → `bedrooms >= X`),
   generic/schema-driven (không hardcode cứng chỉ 2 field, để mở rộng được nếu form thêm field
   sau này). `soft_preferences` (weight/direction/min/max) **KHÔNG** dùng làm điều kiện lọc cứng —
   chỉ đưa vào system prompt của LLM #1 như ngữ cảnh để LLM tự cân nhắc khi chấm điểm. Không dựa
   hoàn toàn vào cách Solution 2 làm (`scoring.filter_hard`) vì có thể không chính xác — tự thiết
   kế generic theo form.
6. **Không dùng MCP protocol thật** (không dựng MCP server/transport riêng) — dùng native
   tool/function-calling chuẩn OpenAI mà OpenRouter proxy lại (`openai` SDK `tools=[...]`), đơn
   giản hơn nhiều so với dựng hạ tầng MCP, khớp tinh thần "không cần agent framework". *(quyết
   định này do assistant đề xuất dựa trên câu trả lời mở "MCP hoặc bất kỳ framework nào" của
   user — cần xác nhận lại nếu user muốn MCP thật.)*
7. **Grounding guardrail (bắt buộc, theo fairness constraint ở trên)**: sau LLM #1, lọc bỏ bất kỳ
   `property_id` nào KHÔNG nằm trong candidate set trả về từ `sql_filter`. Không backfill — nếu
   top5 còn lại <5 thì vẫn hợp lệ theo contract (`top5` được phép <5).

## Scoring prompt design cho LLM #1 (rubric + few-shot compact)

Vì LLM tự chấm `total_score` (không phải công thức deterministic), cần neo thang điểm để giảm
variance giữa các lần gọi — quyết định: **rubric bằng lời + 1-2 few-shot ví dụ compact**, KHÔNG
one-shot/zero-shot thuần túy.

- **Rubric** (đưa vào system prompt bằng lời, không phải code): định nghĩa thang `total_score`
  0.0-1.0 và ý nghĩa từng ngưỡng (>0.8 = rất phù hợp mọi tiêu chí; 0.5-0.8 = phù hợp nhưng có
  đánh đổi rõ; <0.5 = chỉ vừa đạt hard constraint, yếu ở phần soft). Giải thích công thức tham
  chiếu: điểm nên tỉ lệ theo `weight` của từng `soft_preferences` entry và mức độ đáp ứng
  `min`/`max`/`direction` — cho model 1 "gợi ý tính toán" thay vì đoán mò tự do.
- **Few-shot**: 1-2 ví dụ input→output JSON, cố tình dùng **số liệu/case khác hẳn** dữ liệu thật
  (tránh anchoring bias khiến model chỉ "bắt chước" điểm số ví dụ), rút gọn field tối đa (không
  đưa full property object) để không đội context — vì đã tốn context cho tool-calling nhiều turn.
  Mục đích few-shot chỉ để minh họa **format JSON đúng** + **văn phong `reason_tags`/`tradeoff`**,
  không phải để neo điểm số cụ thể.
- Áp dụng: system prompt của `reasoner.py` (turn cuối, lúc ép xuất JSON) sẽ gồm 3 phần: (1) mô tả
  DB schema + tool đã dùng, (2) rubric thang điểm bằng lời, (3) 1-2 few-shot compact minh họa
  format. Cần review lại prompt này kỹ ở Phase 4/8 vì free model dễ không tuân thủ rubric tốt.

## Dựng PostgreSQL + pgvector (cho tool sql_filter; pgvector để dành cho RAG nếu làm sau này)

- Dev local qua Docker Compose: image dựa trên `postgis/postgis:16-3.4` (hoặc `postgres:16` trơn)
  + `CREATE EXTENSION vector` (pgvector) lúc init.
  **Lưu ý**: Docker Desktop cần đang chạy (`open -a Docker` trước nếu daemon chưa start) rồi mới
  `docker compose up -d`.
  PostGIS là **optional/nice-to-have**, không bắt buộc trong plan gốc vì 5 loại tiện ích đã có cột
  khoảng cách tính sẵn từ member-3; PostGIS chỉ hữu ích nếu sau này cần spatial predicate thật
  ngay trong SQL.
- Schema: 1 bảng `properties` với cột khớp danh sách cột đã khóa của member-3 (xem
  [dataset_schema_review.md](../../docs/dataset/dataset_schema_review.md) mục 3). Cột
  `description_embedding vector(N)` KHÔNG cần nữa vì đã bỏ `vector_search` khỏi scope.
- Loader script: đọc `data/go_vap_tan_binh_100_enriched.json`, upsert vào bảng `properties`
  (idempotent, chạy lại nhiều lần an toàn).
- `sql_filter(conditions)`: `conditions` là dict cấu trúc nhỏ (column, op, value), validate theo
  whitelist schema (`schema.py`), dịch sang mệnh đề `WHERE` parameterized (bind qua psycopg,
  **không bao giờ string-concat output của LLM vào SQL** — rủi ro OWASP injection).
- Cần cài `psycopg[binary]` + `pgvector` (thêm vào `requirements.txt`).

## Kiến trúc package (`src/solution1/`)

- `core.py` — `haversine_m` (dùng bởi `get_distance_to_place`; nhân bản riêng, không cross-import)
- `schema.py` — single source of truth mô tả cột DB (tên, kiểu, đơn vị, mô tả, range/enum hợp lệ)
  — dùng để (a) sinh DDL Postgres, (b) sinh đoạn mô tả "database schema" trong system prompt,
  (c) validate whitelist `conditions` của `sql_filter`
- `db.py` — kết nối Postgres, loader (`go_vap_tan_binh_100_enriched.json` → bảng `properties`,
  idempotent upsert), query builder parameterized (whitelist theo `schema.py`)
- `tools.py` — `sql_filter(conditions)` (gọi `db.py`); định nghĩa JSON tool-schema cho LLM
  tool-calling (`sql_filter`, `fetch_nearby_custom`, `get_distance_to_place`)
- `mapbox_client.py` — `geocode_address` (Mapbox Geocoding API), `fetch_nearby_custom` (Tilequery,
  batched theo candidate list, radius tùy chỉnh), `get_distance_to_place` (geocode 1 lần +
  haversine tới từng candidate); cache in-memory; fallback graceful khi thiếu `MAPBOX_TOKEN`
- `llm_client.py` — `OpenRouterLLMClient` (thật, lazy-import `openai`, đọc `OPENROUTER_API_KEY` +
  `SOLUTION1_LLM_MODEL_REASONING` / `SOLUTION1_LLM_MODEL_EXPLANATION` / `SOLUTION1_LLM_MODEL_POOL`
  từ env, rotation/fallback theo stage, ghi lại model nào đã phục vụ mỗi lượt). Không viết
  `MockLLMClient` — dùng key thật để test trực tiếp trong lúc dev.
- `reasoner.py` — LLM #1: bounded tool-calling loop (max 3 turns), ép `sql_filter` ở turn đầu, ép
  JSON output ở turn cuối (`tool_choice="none"`) nếu hết budget; system prompt có rubric + few-shot
  compact (xem mục "Scoring prompt design"); trả `(candidates_json, trace)`
- `guardrail.py` — pure function: grounding filter (loại property_id không thuộc candidate set từ
  `sql_filter`) + dedupe + sort desc `total_score` + renumber rank + cắt `top_k`
- `explainer.py` — LLM #2: single-shot, không tool access, sinh `explanation_summary` (+ optional
  làm giàu narrative mỗi item); template fallback nếu LLM lỗi/timeout (phong cách
  [src/solution2/explanation.py](../solution2/explanation.py))
- `output_contract.py` — map kết quả nội bộ → contract dùng chung, `SOLUTION_ID = "solution_1"`
  (mirror đúng shape của [src/solution2/output_contract.py](../solution2/output_contract.py))
- `pipeline.py` — entrypoint `run(form, free_text, properties, llm_client=None)`: short-circuit
  `status="no_candidate"` nếu `sql_filter` rỗng (không gọi LLM); điều phối
  `reasoner → guardrail → explainer → output_contract`; khi LLM lỗi lặp lại, degrade graceful về
  `status="error"` (vẫn đúng contract) thay vì crash cả batch
- `api.py` — HTTP endpoint local (FastAPI) bọc `pipeline.run`, dùng cho UI tích hợp sau này (xem
  mục "HTTP endpoint cho UI" bên dưới)

**Bỏ hẳn `agent.py` kiểu cũ** (không còn autonomous ReAct loop với điều kiện dừng "diversity ≥ 2
góc nhìn" — thay bằng cap cứng 3 turns ở `reasoner.py`). Bỏ `vector_search`/RAG khỏi scope.

Demo runner: `src/demo/run_solution1.py` (mirror
[src/demo/run_solution2.py](../demo/run_solution2.py)) — load
`data/go_vap_tan_binh_100_enriched.json` + `data/validation_cases_v1.json`, chạy pipeline từng
case với API key thật, in tóm tắt reasoning/top5, ghi `outputs/solution1_results.json` (đúng
contract). Đây là cách chính để verify pipeline trong lúc dev — không viết test suite riêng.

## HTTP endpoint cho UI (sau khi pipeline chạy ổn)

Sau khi pipeline end-to-end chạy ổn định (Phase 7), bọc `pipeline.run` thành **1 HTTP endpoint
chạy local** để UI (mới hoặc UI đã có sẵn của nhóm) gọi vào:

- Dùng **FastAPI** (nhẹ, tự sinh OpenAPI docs, dễ chạy local qua `uvicorn`) — thêm `fastapi` +
  `uvicorn` vào `requirements.txt`.
- 1 route chính: `POST /solution1/recommend` — nhận body `{form, free_text}`, trả về JSON đúng
  `output_contract` (field `case_id` có thể để optional/tự sinh nếu UI không truyền).
- Chạy local: `uvicorn src.solution1.api:app --reload --port <port>` (chọn port cụ thể lúc code,
  tránh đụng port UI khác nếu có).
- CORS: nếu UI chạy ở origin khác (vd dev server React/Vite) cần bật `CORSMiddleware` với origin
  whitelist rõ ràng (không dùng `"*"` bừa bãi — theo OWASP, tránh mở CORS cho mọi origin).
- Validate input ở boundary (Pydantic model cho `form`/`free_text`) trước khi đưa vào
  `pipeline.run`, tránh lỗi mơ hồ khi UI gửi thiếu field.
- Đây là **Phase riêng, làm SAU khi Phase 0-8 (pipeline core) đã chạy ổn** — không làm song song,
  vì cần pipeline output ổn định trước khi thiết kế response shape cho UI.

## Triển khai theo phase (không viết test suite — verify bằng cách chạy pipeline thật với API key thật)

0. **Scaffolding + khóa contract**: skeleton package, `core.py`, `schema.py`, `output_contract.py`.
   Verify: chạy thử `pipeline.run()` với 1 fixture nhỏ, in ra JSON, kiểm tra bằng mắt đúng field
   bắt buộc của contract (chưa cần Postgres/LLM thật ở bước này nếu chưa sẵn sàng).
1. **`sql_filter` + dựng Postgres** *(có thể song song với Phase 2, 3)*: `docker-compose.yml`
   (postgres), `schema.py` → DDL, `db.py` loader + query builder whitelist, `sql_filter()`
   query Postgres thật.
   Verify: chạy loader thật (`docker compose up -d db` trước), gọi `sql_filter()` với vài điều
   kiện mẫu, in kết quả ra xem đúng số lượng/đúng property — chạy lại loader nhiều lần để tự kiểm
   tra idempotent bằng mắt.
2. **`mapbox_client.py`** *(song song với Phase 1, 3)*: `geocode_address`, `fetch_nearby_custom`,
   `get_distance_to_place` (batched theo candidate list), dùng `MAPBOX_TOKEN` thật ngay từ đầu.
   Verify: chạy thử trực tiếp với vài địa chỉ/tọa độ thật, in kết quả, kiểm tra bằng mắt khoảng
   cách/số lượng POI hợp lý.
3. **`llm_client.py`** *(song song với Phase 1, 2)*: `OpenRouterLLMClient` (rotation pool, model
   riêng theo stage), dùng `OPENROUTER_API_KEY` thật ngay từ đầu.
   Verify: gọi thử 1 request tool-calling đơn giản, in response, kiểm tra model nào trả lời + có
   đúng `tool_calls` không.
4. **`reasoner.py`** (phụ thuộc 1, 2, 3): bounded tool-calling loop, system prompt schema-aware +
   soft_preferences context + rubric thang điểm + 1-2 few-shot compact.
   Verify: chạy `--dry-run` với vài case thật (lấy từ `validation_cases_v1.json`), in full
   reasoning trace + model nào đã phục vụ mỗi lượt, xem bằng mắt tool có được gọi đúng thứ tự
   (sql_filter trước) và JSON cuối có đúng format không.
5. **`guardrail.py`** *(độc lập, code thuần — có thể làm song song với Phase 4)*.
   Verify: chạy thử với 1 JSON candidates giả có chèn 1 property_id không hợp lệ, kiểm tra bằng
   mắt nó bị lọc, thứ tự/rank đúng.
6. **`explainer.py`** (phụ thuộc 3): single-shot LLM #2 với API key thật.
   Verify: chạy thử với top5 mẫu, đọc `explanation_summary` sinh ra xem có hợp lý/tiếng Việt tự
   nhiên không.
7. **Nối end-to-end**: `pipeline.py` (reasoner → guardrail → explainer → contract),
   `src/demo/run_solution1.py`.
   Verify: `python3 src/demo/run_solution1.py` chạy thật (API key thật) toàn bộ
   `data/validation_cases_v1.json` (cần Postgres local đang chạy), ra `outputs/solution1_results.json`;
   đọc qua output bằng mắt, so sánh shape với `outputs/solution2_results.json`.
8. **Tinh chỉnh**: xem lại reasoning trace của vài case, review kỹ rubric scoring có hợp lý không
   (không dồn cụm điểm bất thường), tinh chỉnh system prompt/tool description dựa trên quan sát
   thực tế từ Phase 7.
9. **HTTP endpoint cho UI** (làm SAU khi Phase 0-8 đã ổn định): implement `api.py` (FastAPI),
   chạy `uvicorn` local, test bằng `curl`/Postman gọi `POST /solution1/recommend`, xác nhận response
   đúng contract và CORS/validate input hoạt động đúng trước khi bàn giao cho UI.

## Cần lưu ý thêm / rủi ro

1. LLM tự chấm điểm → kết quả không deterministic/reproducible như Solution 2 — chấp nhận được
   theo quyết định của user, nhưng validation/so sánh giữa 2 solution cần biết trước điều này
   (`total_score` có thể lệch nhau về THANG ĐO, không chỉ về thứ tự).
2. Không có test suite tự động → mọi thay đổi ở `reasoner.py`/`explainer.py`/prompt cần được
   review thủ công bằng cách chạy lại `src/demo/run_solution1.py` với vài case thật và đọc trace —
   rủi ro regression âm thầm cao hơn so với có test, cần cẩn thận khi sửa system prompt.
3. Free model tool-calling có thể không ổn định ở turn ép cuối (`tool_choice="none"`) — cần quan
   sát kỹ khi chạy thật ở Phase 4/7, có fallback parse JSON lỏng (regex/extract) nếu model trả
   text lẫn JSON.
4. Việc "ép JSON ở turn cuối" cần schema JSON rõ ràng (JSON mode hoặc `response_format`) —
   OpenRouter một số free model có thể không hỗ trợ `response_format=json_schema` → cần fallback
   parse.
5. Guardrail lọc property_id hallucinated có thể làm top5 <5 phần tử nếu model bịa nhiều — hợp lệ
   theo contract nhưng cần log rõ để debug tại sao.
6. Mapbox có rate limit — nên cache theo `(lat, lon, amenity)` / `(address)` để chạy lại 50+
   validation case nhiều lần khi dev không tốn quota (quan trọng hơn khi không có mock để thay
   thế network call lúc lặp lại thử nghiệm).
7. Dựng Postgres là hạ tầng local mới cho nhóm — cần Docker Desktop đang chạy trước khi
   `docker compose up -d`; các thành viên khác cũng cần Docker + cùng `docker-compose.yml` để
   chạy Solution 1 ở máy họ.
8. Quyết định "không dùng MCP thật" là lựa chọn của assistant dựa trên câu trả lời mở của user
   ("MCP hoặc bất kỳ framework nào") — cần xác nhận lại nếu user muốn dựng MCP server/transport
   thật thay vì native tool-calling.
9. HTTP endpoint (Phase 9) chỉ nên bắt đầu sau khi pipeline core (Phase 0-8) đã chạy ổn định với
   nhiều case thật — tránh phải đổi response shape giữa chừng khi UI đã bắt đầu tích hợp.

## Trạng thái

Redesign đã được thảo luận và chốt qua nhiều vòng hỏi-đáp với user (Phu, member-1), bao gồm quyết
định mới: bỏ test suite/UT chính thức (dùng API key thật để test trực tiếp trong lúc dev), và
thêm Phase 9 (HTTP endpoint FastAPI) để chuẩn bị tích hợp UI sau khi pipeline core ổn định. Plan
đã cập nhật đầy đủ theo flow tuần tự 2-LLM mới. Sẵn sàng bắt đầu triển khai từ Phase 0 khi user
cung cấp `OPENROUTER_API_KEY` + `MAPBOX_TOKEN` thật.
