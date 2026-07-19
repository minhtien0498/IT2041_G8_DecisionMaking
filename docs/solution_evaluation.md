# Solution Evaluation - Smart Real Estate Advisory System

File này đánh giá hai solution final hiện tại và gợi ý cách trình bày với thầy.

Ghi chú cập nhật:

- `Solution 1`: pipeline tuần tự hai LLM có guardrail của `Phú`.
- `Solution 2`: hybrid form + free-text + map enrichment của `Quang`.
- Hướng rule-based cũ và bản đề xuất MCDA/TOPSIS cũ không còn là scope final active.

## 1. Summary

| Solution | Short name | Core idea | Recommendation |
|---|---|---|---|
| Solution 1 | Two-LLM + Guardrail | Form + free-text -> LLM reasoner gọi tool -> guardrail grounding -> LLM explainer | Một hướng final chính, mạnh về reasoning có kiểm soát |
| Solution 2 | Hybrid LLM + Mapbox enrichment | Form + free-text -> LLM parser -> enrich POI bằng Mapbox -> deterministic re-rank -> explanation | Một hướng final chính, mạnh về scoring rõ ràng và cá nhân hóa |

## 2. Solution 1 Evaluation

### Pipeline

```text
Form + Free-text
-> Hard constraints
-> LLM reasoner + sql_filter
-> Optional dynamic enrichment
-> Candidate scoring by LLM
-> Guardrail grounding
-> Top 5
-> LLM explanation
```

### Strengths

- Linh hoạt với nhu cầu tự nhiên vì LLM reasoner có thể quyết định khi nào cần gọi tool.
- Có guardrail grounding nên Top 5 không được bịa ngoài dataset.
- Có thể enrich thêm tiện ích động `Y` khi free-text nhắc đến nhu cầu chưa có trong nhóm tiện ích nền `X`.
- Explanation sâu hơn, phù hợp để demo trade-off giữa các lựa chọn.
- Output hiện đã có 10 validation case sơ bộ trong `outputs/solution1_results.json`.

### Weaknesses

- Latency cao vì mỗi case có thể gọi nhiều lượt LLM/tool.
- Explanation có thể quá dài, có lỗi ngôn ngữ hoặc suy diễn ngoài dữ liệu nếu không review.
- Cần API key và môi trường Postgres/OpenRouter/Mapbox để chạy đầy đủ.
- Validation phải ghi rõ case nào đánh giá trên `X` và case nào đánh giá trên `X + Y`, nếu không dễ thiếu công bằng.

### Metrics nên dùng

| Metric | Meaning |
|---|---|
| Constraint satisfaction | Top 5 có vi phạm hard constraints không |
| Grounding Pass Rate | Top 5 có thuộc candidate set/database không |
| Tool-call correctness | LLM có gọi đúng tool khi free-text cần enrichment không |
| Dynamic enrichment usefulness | Thuộc tính `Y` có thật sự cải thiện relevance không |
| Explanation faithfulness | Explanation có bám đúng Top 5 và thuộc tính thật không |
| Latency | Có đủ ổn để demo/batch validation không |

### Verdict

Solution 1 nên được giữ như một hướng final chính, nhưng cần trình bày đúng bản chất: đây không phải phương pháp MCDA/TOPSIS, mà là **LLM tool-use có guardrail dữ liệu**. Khi bảo vệ, nên nhấn mạnh rằng LLM được dùng cho reasoning và giải thích, còn code chịu trách nhiệm khóa biên dữ liệu, hard constraints và grounding.

## 3. Solution 2 Evaluation

### Pipeline

```text
Form + Additional User Request
-> LLM Requirement Parsing
-> Deduplication with Form Criteria
-> Amenity Mapping
-> Rule-based Top 10
-> Tool-based Attribute Enrichment
-> Re-scoring / Re-ranking
-> Top 5
-> LLM Explanation
```

### Strengths

- Hợp tinh thần "thông minh" vì hiểu được nhu cầu tự nhiên.
- Ranking cuối do inference engine tính toán nên dễ debug hơn Solution 1.
- Tách rõ parser, enrichment, scoring và explanation.
- Có thể xử lý nhu cầu như gần trường mẫu giáo, nhiều quán cafe, gần chợ, gần bệnh viện.
- Dễ trình bày như một lớp mở rộng trên form cố định.

### Weaknesses

- Phụ thuộc API map/geocoding nếu chưa có lat/lon và POI.
- LLM parser có thể hiểu sai nhu cầu hoặc map sai amenity.
- Nếu chỉ enrich Top 10 sau base scoring, có thể bỏ sót listing ngoài Top 10 nhưng rất phù hợp với nhu cầu bổ sung.
- Cần cache để kết quả demo và validation tái lập.

### Metrics nên dùng

| Metric | Meaning |
|---|---|
| Intent parsing accuracy | LLM parse nhu cầu đúng không |
| Amenity mapping accuracy | Nhu cầu có map đúng sang POI/feature không |
| Re-ranking usefulness | Ranking sau enrichment có hợp lý hơn không |
| Explanation faithfulness | LLM giải thích có dựa đúng score/attribute không |
| Latency/cost | Có chạy được trong demo không |

### Verdict

Solution 2 nên được giữ như hướng final chính còn lại. Đây là hướng có scoring engine rõ hơn, dễ kiểm chứng hơn, nhưng parser và enrichment cần được khóa schema/capability để tránh sinh tiêu chí không đo được.

## 4. So sánh hai solution

| Tiêu chí | Solution 1 | Solution 2 |
|---|---|---|
| Bản chất | LLM reasoning + tool-use + guardrail | LLM parser + deterministic scoring/re-ranking |
| Vai trò LLM | Reasoning, gọi tool, chấm điểm sơ bộ, giải thích | Parse nhu cầu và giải thích |
| Kiểm soát ranking | Guardrail sau LLM | Inference engine tính điểm trực tiếp |
| Linh hoạt free-text | Cao | Cao nhưng phụ thuộc parser schema |
| Reproducibility | Trung bình, phụ thuộc LLM/API | Tốt hơn nếu cache enrichment |
| Latency | Cao hơn | Thường thấp hơn |
| Risk chính | Explanation dài/sai, tool-call chưa đúng, latency cao | Parser sai, POI thiếu, re-rank lệch |
| Validation cần thêm | Grounding, tool-call correctness, X+Y relevance | Intent parsing, mapping accuracy, re-ranking usefulness |

## 5. Presentation Recommendation

Khi trình bày với thầy, nên nói:

1. Hướng rule-based cũ đã bị loại vì quá giống bộ lọc nâng cao.
2. Nhóm giữ hai hướng final:
   - `Solution 1`: LLM tool-use có guardrail, mạnh về reasoning có kiểm soát.
   - `Solution 2`: hybrid parser + enrichment + scoring, mạnh về scoring minh bạch hơn.
3. Cả hai solution đều dùng chung dataset 100 căn và output contract chung.
4. Với Solution 1, cần nói rõ Top 5 luôn thuộc database, không để LLM bịa property.
5. Với validation, cần ghi rõ tiêu chí nền `X` và tiêu chí enrich động `Y`.

## 6. Suggested Final Scope

Scope nên chốt:

```text
100 listings Gò Vấp + Tân Bình
3-5 amenity types nền
10-50 validation scenarios tùy thời gian
Top 5 recommendation
Explanation dựa trên dữ liệu thật
Comparison bằng CSR, NDCG@5, MAP@5, human relevance, latency và explanation faithfulness
```
