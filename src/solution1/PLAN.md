# Plan: Solution 1 as LLM ReAct Agent (thay thế bản rule-based cũ)

> Solution 1 chính thức = [docs/source_notes/Solution-1-Detail.md](../../docs/source_notes/Solution-1-Detail.md)
> (LLM Agent, tool-use, ReAct loop) — KHÔNG phải [docs/Solution-1-Detail.md](../../docs/Solution-1-Detail.md)
> (bản rule-based cũ). Solution 2 giữ nguyên, không đổi.

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
2 solution. Các hàm toán dùng chung (`haversine_m`, `normalize_score`) được nhân bản riêng ở mỗi
package.

Test suite **không được yêu cầu API key thật** (mock LLM + mock HTTP Mapbox), đúng convention
"deterministic offline" đã có ở [tests/test_pipeline_contract.py](../../tests/test_pipeline_contract.py).

## Quyết định đã chốt (qua 2 vòng trao đổi với user)

- **LLM**: OpenRouter (dùng lại `openai` SDK, `base_url=https://openrouter.ai/api/v1`). Dùng
  **rotation pool** thay vì 1 model cố định để tránh rate-limit free-tier và so sánh hiệu quả:
  - `openai/gpt-oss-20b:free` (mặc định, tool-calling native, nhẹ)
  - `qwen/qwen3-coder:free` (đã xác nhận hỗ trợ tool-calling native qua trang model OpenRouter)
  - `nvidia/nemotron-3-super-120b-a12b:free`, `nvidia/nemotron-3-ultra-550b-a55b:free` (agentic/orchestration)
  - `openai/gpt-oss-120b:free` — fallback mạnh hơn (optional)
  - **Không dùng gpt-4o-mini** (trả phí, không free; hiện chưa ai trong nhóm lock model nào —
    `requirement_parser` của Solution 2 vẫn deterministic, chưa gọi LLM thật).
  - `llm_client.py`'s `OpenRouterLLMClient` thử model chính, tự fallback sang model kế tiếp trong
    pool khi lỗi/429, và **ghi lại model nào đã phục vụ mỗi lần gọi** (trong agent trace) để so
    sánh hiệu quả sau. Override qua env: `SOLUTION1_LLM_MODEL` (1 model) hoặc
    `SOLUTION1_LLM_MODEL_POOL` (danh sách, phân tách bằng dấu phẩy).
- **RAG (ghi chú cho sau, `vector_search` vẫn PENDING)**: dùng
  `nvidia/llama-nemotron-embed-vl-1b-v2:free` trên OpenRouter khi làm `vector_search` thật
  (embedding đa phương thức text+image, free). Lưu ý: free endpoint của OpenRouter log lại toàn
  bộ prompt/output ("trial use only") — chấp nhận được với mô tả nhà (không nhạy cảm).
- Bắt buộc có **Mock LLM + Mock Mapbox client** cho unit test/CI (không cần network/API key thật).
- `fetch_nearby(lat, lon, amenity, radius_m)` → **Mapbox Tilequery API** (query lớp POI trên vector
  tile quanh 1 điểm, đơn giản hơn Search Box/Category Search, không cần session token).
- `get_distance` → **đã suy nghĩ lại** theo câu hỏi của user ("phương tiện có ảnh hưởng lúc search
  không, hay chỉ lúc đánh giá?"). Trả lời: route distance thật (Mapbox Directions) có phụ thuộc
  phương tiện và khác với đường chim bay, nhưng với mục đích search/reasoning của agent thì đường
  chim bay (haversine) là đủ — mode-agnostic, nhất quán với cách member-3 đã enrich, và không tốn
  quota Mapbox mỗi bước suy luận.
  → **Quyết định**: `get_distance(a, b)` ở tool layer chỉ trả **haversine thuần túy**, không cần
  tham số `profile` lúc search. Mapbox Directions thật (phụ thuộc phương tiện: `walking` cho
  trường/công viên/bệnh viện/nhà thuốc, `driving` làm proxy cho xe máy với siêu thị/chợ/gym) được
  **dời sang lớp enrichment/explanation sau này** (vd: "khoảng X phút đi bộ/xe" hiển thị cho
  người dùng), KHÔNG nằm trong core ReAct search loop.
- `sql_filter`: **cần datastore thật** → dựng **PostgreSQL** (xem mục riêng bên dưới) thay vì lọc
  in-memory trên JSON, theo yêu cầu của user (có pgvector cho RAG sau này).
- **Schema-aware agent**: duy trì DUY NHẤT 1 bản mô tả schema (Python, single source of truth):
  tên cột, kiểu, đơn vị, mô tả, range/enum hợp lệ — dùng để (a) sinh DDL Postgres, (b) sinh đoạn
  mô tả "database schema" trong system prompt để ReAct agent biết được lọc trên cột nào, và (c)
  validate (whitelist) argument `conditions` của `sql_filter` trước khi build SQL parameterized
  (không bao giờ string-concat output của LLM vào SQL — rủi ro OWASP injection). Nội dung gốc lấy
  từ danh sách "cột bắt buộc" ở
  [docs/dataset/dataset_schema_review.md](../../docs/dataset/dataset_schema_review.md).
- **Dataset**: `data/go_vap_tan_binh_100_enriched.json` (không dùng bộ legacy 37 căn) — load vào Postgres.
- **Env**: file `.env` mới (gitignored) chứa `OPENROUTER_API_KEY`, `MAPBOX_TOKEN`, `DATABASE_URL`,
  load qua `python-dotenv` (đã có sẵn trong `requirements.txt`). Thêm `requests`,
  `psycopg[binary]`, `pgvector` vào `requirements.txt`.
- **Tool layer** chia làm 3 sub-phase nhỏ để dễ review (1 review / 1 function):
  1. `sql_filter` + dựng Postgres (schema, loader, query builder whitelist) — phần lớn nhất
  2. `fetch_nearby` (Mapbox Tilequery)
  3. `get_distance` (haversine thuần túy theo quyết định trên)

## Dựng PostgreSQL + pgvector (cho tool sql_filter + RAG sau này)

- Dev local qua Docker Compose: image dựa trên `postgis/postgis:16-3.4` (hoặc `postgres:16` trơn)
  + `CREATE EXTENSION vector` (pgvector) lúc init.
  **Lưu ý**: Docker Desktop đã cài trên máy nhưng daemon **chưa chạy** lúc kiểm tra (`docker info`
  fail) — cần `open -a Docker` và đợi khởi động xong trước khi `docker compose up -d`.
  PostGIS là **optional/nice-to-have** (xem mục "Cần lưu ý thêm"), không bắt buộc trong plan gốc
  vì 5 loại tiện ích đã có cột khoảng cách tính sẵn từ member-3; PostGIS chỉ hữu ích nếu sau này
  cần spatial predicate thật (vd: "trong bán kính X quanh điểm Y") ngay trong `sql_filter`.
- Schema: 1 bảng `properties` với cột khớp danh sách cột đã khóa của member-3 (xem
  [dataset_schema_review.md](../../docs/dataset/dataset_schema_review.md) mục 3) + 1 cột
  `description_embedding vector(N)` nullable, để dành cho RAG (chưa điền cho tới khi làm
  `vector_search`).
- Loader script: đọc `data/go_vap_tan_binh_100_enriched.json`, upsert vào bảng `properties`
  (idempotent, chạy lại nhiều lần an toàn).
- `sql_filter(conditions)`: `conditions` là dict cấu trúc nhỏ (column, op, value), validate theo
  whitelist schema ở trên, dịch sang mệnh đề `WHERE` parameterized (bind qua psycopg, không string
  format thô) — vd `{"price_million_vnd": {"lte": 8000}, "bedrooms": {"gte": 3}}`.
- Đã kiểm tra: `psycopg2`/`sqlalchemy`/`pgvector` **chưa cài** trong môi trường hiện tại — cần
  `pip install` ở bước 1a.

## Kiến trúc (package mới `src/solution1/`, mirror layout của `src/solution2/`)

- `core.py` — `haversine_m`, `normalize_score` (nhân bản riêng, không cross-import)
- `tools.py` — `sql_filter(properties, conditions)`; `vector_search()` stub/pending
- `mapbox_client.py` — wrapper HTTP: `fetch_nearby` (Tilequery), có cache in-memory theo
  `(lat, lon, amenity)` làm tròn để tiết kiệm quota; fallback graceful (raise
  `MapboxUnavailableError` / trả `None`) khi thiếu `MAPBOX_TOKEN`, để pipeline có thể fallback về
  cột `distance_to_nearest_*` có sẵn của member-3 thay vì crash
- `llm_client.py` — `LLMClient` (interface); `MockLLMClient` (scripted/deterministic, cho test);
  `OpenRouterLLMClient` (thật, lazy-import `openai`, đọc `OPENROUTER_API_KEY` +
  `SOLUTION1_LLM_MODEL(_POOL)` từ env, mặc định `openai/gpt-oss-20b:free`, có rotation/fallback)
- `agent.py` — ReAct loop (Reason→Act→Observe), tool registry/dispatch, giới hạn an toàn số lần
  gọi tool (vd 8), điều kiện dừng theo diversity (≥2 góc nhìn), system prompt + few-shot lấy từ
  [Solution-1-Detail.md](../../docs/source_notes/Solution-1-Detail.md), có inject schema database
- `explanation.py` — sinh giải thích tiếng Việt từ agent trace + top5 (có template fallback khi ở
  mock mode, theo phong cách [src/solution2/explanation.py](../solution2/explanation.py))
- `output_contract.py` — map kết quả nội bộ → contract dùng chung, `SOLUTION_ID = "solution_1"`
  (mirror đúng shape của [src/solution2/output_contract.py](../solution2/output_contract.py))
- `pipeline.py` — entrypoint `run(form, free_text, properties, llm_client=None)`; chọn
  `OpenRouterLLMClient` nếu có `OPENROUTER_API_KEY` else `MockLLMClient` (hoặc override qua
  `SOLUTION1_LLM_MODE=mock|live`); khi agent lỗi lặp lại, degrade graceful về `status="error"`
  (vẫn đúng contract) thay vì crash cả batch

Demo runner mới: `src/demo/run_solution1.py` (mirror
[src/demo/run_solution2.py](../demo/run_solution2.py)) — load
`data/go_vap_tan_binh_100_enriched.json` + `data/validation_cases_v1.json`, chạy pipeline từng
case, in tóm tắt reasoning/top5, ghi `outputs/solution1_results.json` (đúng contract).

Test mới (mirror pattern của
[tests/test_pipeline_contract.py](../../tests/test_pipeline_contract.py), không network/API thật):
- `tests/test_solution1_tools.py` — logic `sql_filter`; `mapbox_client` build URL/parse
  response/cache với `requests.get` bị monkeypatch (không cần token/network)
- `tests/test_solution1_agent.py` — ReAct loop chạy end-to-end qua `MockLLMClient` (tool call kịch
  bản sẵn), verify điều kiện dừng/diversity/giới hạn số lần gọi tool
- `tests/test_solution1_pipeline_contract.py` — đúng shape/thứ tự contract, cùng kiểu check
  `REQUIRED_TOP_FIELDS`/`REQUIRED_TOP5_FIELDS` như test của Solution 2, chạy với dataset 100 căn +
  `validation_cases_v1.json` mẫu, dùng `MockLLMClient`

## Triển khai theo phase (mỗi phase tự chạy/tự verify được, không cần chờ agent hoàn chỉnh)

0. **Scaffolding + khóa contract**: skeleton package, `core.py`, `output_contract.py`, 1 bản
   `pipeline.run()` tạm chỉ làm `sql_filter` (in-memory, tạm thời) + scoring cơ bản (chưa LLM) để
   chứng minh tương thích contract ngay.
   Verify: `pytest tests/test_solution1_pipeline_contract.py` xanh.
1. **`sql_filter` + dựng Postgres**: `docker-compose.yml` (postgres+pgvector), schema.sql / module
   mô tả schema, loader script (JSON enriched → bảng `properties`), query builder whitelist,
   `sql_filter()` giờ query Postgres thật.
   Verify: `pytest tests/test_solution1_tools.py::test_sql_filter*` xanh với Postgres local thật
   (`docker compose up -d db` trước); loader chạy lại nhiều lần vẫn idempotent.
2. **`fetch_nearby` (Mapbox Tilequery)**: implement `mapbox_client.fetch_nearby` + cache.
   Verify: `pytest tests/test_solution1_tools.py::test_fetch_nearby*` xanh với `requests.get` bị
   monkeypatch, không cần API key.
3. **`get_distance` (haversine thuần)**: implement trong `core.py` hoặc `mapbox_client.py` (không
   cần gọi Mapbox thật theo quyết định ở trên).
   Verify: `pytest tests/test_solution1_tools.py::test_get_distance*` xanh, unit test thuần không
   network.
4. **LLM client + agent loop**: `llm_client.py` (Mock + OpenRouter có rotation pool), `agent.py`
   ReAct loop, system prompt schema-aware (inject mô tả DB schema + few-shot từ
   Solution-1-Detail.md).
   Verify: `pytest tests/test_solution1_agent.py` xanh qua `MockLLMClient`; có script `--dry-run`
   in full reasoning trace + model nào đã phục vụ mỗi lượt.
5. **Nối end-to-end**: `pipeline.run` nhánh thật, `explanation.py`, `src/demo/run_solution1.py`.
   Verify: `python3 src/demo/run_solution1.py` chạy ở mock mode (không cần key, nhưng cần Postgres
   local đang chạy), ra `outputs/solution1_results.json` đúng contract.
6. **Live smoke test**: sau khi user cung cấp `OPENROUTER_API_KEY` + `MAPBOX_TOKEN` trong `.env`,
   chạy thật vài case, xem lại reasoning trace, tinh chỉnh system prompt/tool description, so sánh
   shape của `outputs/solution1_results.json` với `outputs/solution2_results.json`.

## Cần lưu ý thêm

1. Free model trên OpenRouter có thể tool-calling không ổn định — pipeline nên catch lỗi agent và
   trả `status="error"` (vẫn đúng contract) thay vì crash cả batch validation. Rotation pool giúp
   giảm bớt vấn đề rate-limit cụ thể.
2. Mapbox free tier có rate limit — nên cache theo `(lat, lon, amenity)` để chạy lại 50+ validation
   case nhiều lần khi dev không tốn quota.
3. PostGIS (spatial predicate trong SQL) là optional add-on, chưa cần trong plan gốc — chỉ đáng
   thêm nếu sau này nhóm muốn "BĐS trong bán kính X quanh điểm Y" như 1 điều kiện `sql_filter`
   sống, vượt ra ngoài 5 khoảng cách tiện ích đã tính sẵn.
4. Dựng Postgres là hạ tầng local mới cho nhóm — cần Docker Desktop đang chạy (`open -a Docker`
   trước) rồi mới `docker compose up -d`; các thành viên khác cũng cần Docker + cùng
   `docker-compose.yml` để chạy Solution 1 ở máy họ (trước đây không cần vì Solution 2 và
   validation là JSON/in-memory thuần túy).

## Trạng thái

Plan đã trình bày và được duyệt bởi user (Phu, member-1). Sẵn sàng bắt đầu triển khai từ Phase 0.
