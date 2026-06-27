## Solution 1 — Form + Free-Text → LLM Agent (Tool Use) → Top 5 + Explanation

```mermaid
flowchart TD
    subgraph INPUT["Input (chung cho cả 2 solution)"]
        A["📋 Form cố định\nNgân sách · Số phòng · Khoảng cách"]
        B["💬 Nhu cầu thêm _(tùy chọn)_\nMô tả tự do"]
    end

    subgraph TOOLS["🔧 Tools được khai báo"]
        T1["sql_filter()\nRelational DB"]
        T2["vector_search()\nVector DB"]
        T3["fetch_nearby()\nMap API — tiện ích xung quanh"]
        T4["get_distance()\nKhoảng cách đến địa điểm"]
    end

    INPUT --> C["🧠 LLM Agent\n(System Prompt + Few-shot)"]
    TOOLS -. available .-> C

    subgraph LOOP["🔄 ReAct Loop"]
        R["Reason\nLên kế hoạch, quyết định tool"]
        AC["Act\nGọi tool"]
        OB["Observe\nĐánh giá — Đủ đa dạng chưa?"]
        R --> AC --> OB
        OB -->|Chưa đủ| R
    end

    C --> LOOP

    OB -->|Đủ rồi / đạt giới hạn| E["🏆 Chọn Top 5 đa dạng\nTừ nhiều góc nhìn khác nhau"]

    E --> F["💡 LLM Explanation\nGiải thích tradeoff\nGợi ý theo tín hiệu nhu cầu"]
```

**Điểm cốt lõi của Solution 1:**
- LLM Agent tự quyết định chiến lược — không có pipeline cứng.
- Kết hợp linh hoạt nhiều tool: SQL filter, vector search, Map API, distance.
- Vòng lặp ReAct cho phép khám phá nhiều góc nhìn và dừng khi đã đủ đa dạng.
- Chất lượng suy luận được tinh chỉnh qua system prompt và few-shot examples.

---

## Solution 2 — Form + Free-Text → Inference Engine + LLM Enrichment → Top 5

```mermaid
flowchart TD
    subgraph INPUT["Input (chung cho cả 2 solution)"]
        A["📋 Form cố định\nNgân sách · Số phòng · Khoảng cách tiện ích"]
        B["💬 Nhu cầu thêm _(tùy chọn)_\nMô tả tự do bằng ngôn ngữ tự nhiên"]
    end

    A --> C["⚙️ Inference Engine\nRule-based Filtering + Scoring\ndựa trên form"]
    C --> D["📋 Top 10 ban đầu\n+ base score từ form"]

    B --> E["🧠 LLM Requirement Parsing\nPhân tích nhu cầu thêm"]
    E --> E1["✅ Hard constraints mới"]
    E --> E2["⭐ Soft preferences mới"]
    E --> E3["🚫 Unsupported → gắn cờ\nkhông đưa vào scoring"]

    E2 --> F["🗺️ Amenity Mapping\nQuy đổi sang tên tiện ích\nmarket · cafe · kindergarten…"]

    D --> G["📍 Enrichment\nGeocode địa chỉ → lat, long\nSearch Map API → count + distance"]
    F --> G

    G --> H["🆕 Sinh thuộc tính động\nCho toàn bộ Top 10"]

    H --> I["🔒 Post-filtering\nÁp hard constraints mới"]
    E1 --> I

    I --> J["📊 Re-scoring\nfinal = α × base_score + β × additional_score"]
    D --> J

    J --> K["🏆 Re-ranking → Top 5"]

    K --> L["💡 LLM Explanation\nGiải thích thay đổi thứ hạng\nSo sánh điểm nền vs điểm bổ sung"]
```

**Điểm cốt lõi của Solution 2:**
- Inference Engine làm backbone — kết quả ổn định, dễ kiểm chứng và debug.
- LLM chỉ mở rộng tiêu chí, không thay thế engine → kiểm soát tốt hơn.
- Enrichment qua Map API cho phép đo lường chính xác các tiện ích xung quanh.
- Trọng số α, β kiểm soát mức ảnh hưởng giữa form gốc và nhu cầu thêm (khuyến nghị α=0.7, β=0.3).
- Phù hợp khi nhu cầu thêm có thể quy đổi thành amenity name cụ thể (chợ, café, trường mẫu giáo…).

