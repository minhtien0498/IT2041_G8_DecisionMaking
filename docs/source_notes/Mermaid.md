## Solution 1 — Form + Free-Text → Two-LLM Pipeline + Guardrail

```mermaid
flowchart TD
    subgraph INPUT["Input"]
        A["Form cố định\nNgân sách · Số phòng · khu vực"]
        B["Free-text\nNhu cầu tự nhiên"]
    end

    A --> C["Hard constraints\nsinh bằng code"]
    B --> D["LLM Reasoner"]
    C --> D

    subgraph TOOLS["Tools"]
        T1["sql_filter()\nlọc candidate trong DB"]
        T2["fetch_nearby_custom()\nenrich tiện ích động"]
        T3["get_distance_to_place()\nkhoảng cách đến địa điểm cụ thể"]
    end

    TOOLS -. tool use .-> D
    D --> E["Candidates + total_score\nreason_tags · tradeoff"]
    E --> F["Guardrail grounding\nlọc ID ngoài DB · dedupe · sort · Top 5"]
    F --> G["LLM Explainer\nkhông gọi tool, không đổi rank"]
    G --> H["Output contract chung"]
```

**Điểm cốt lõi của Solution 1:**

- LLM reasoner được phép gọi tool nhưng bị giới hạn trong candidate set.
- Guardrail bằng code đảm bảo Top 5 luôn thuộc dataset.
- Enrichment động chỉ bổ sung thuộc tính cho candidate, không mở rộng tập bất động sản.
- LLM explainer chỉ diễn giải Top 5 đã được khóa.

---

## Solution 2 — Form + Free-Text → Inference Engine + LLM Enrichment → Top 5

```mermaid
flowchart TD
    subgraph INPUT["Input"]
        A["Form cố định\nNgân sách · Số phòng · khoảng cách tiện ích"]
        B["Free-text\nMô tả nhu cầu tự nhiên"]
    end

    A --> C["Inference Engine\nFiltering + Scoring"]
    C --> D["Top 10 ban đầu\nbase score"]

    B --> E["LLM Requirement Parsing"]
    E --> F["Amenity Mapping"]
    F --> G["POI Enrichment"]
    D --> G

    G --> H["Post-filtering\nRe-scoring / Re-ranking"]
    H --> I["Top 5"]
    I --> J["LLM Explanation"]
```
