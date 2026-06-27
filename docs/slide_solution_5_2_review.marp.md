---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Solution 5.2 · Xin ý kiến Thầy'
footer: 'Nhóm 8 (IT2041_G8) · DSS with Data'
style: |
  section {
    background: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 24px;
    padding: 50px 60px;
  }
  section h1 { color: #1d4ed8; font-size: 40px; margin-bottom: 6px; }
  section h2 { color: #b45309; font-size: 26px; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; margin-top: 4px; }
  section h3 { color: #1d4ed8; font-size: 22px; }
  section header { color: #64748b; font-size: 14px; }
  section footer { color: #94a3b8; font-size: 13px; }
  section strong { color: #b45309; }
  section em { color: #1d4ed8; font-style: normal; font-weight: 600; }
  table { font-size: 17px; border-collapse: collapse; width: 100%; margin-top: 8px; }
  th { background: #1d4ed8; color: #fff; padding: 7px 10px; text-align: left; }
  td { background: #fff; padding: 6px 10px; border-bottom: 1px solid #e2e8f0; }
  code { background: #e2e8f0; color: #b45309; padding: 1px 6px; border-radius: 4px; font-size: 0.9em; }
  pre { background: #0f172a; color: #e2e8f0; border-radius: 8px; font-size: 15px; }
  blockquote { border-left: 4px solid #b45309; background: #fffbeb; color: #78350f; padding: 10px 16px; border-radius: 4px; font-style: normal; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
  .card { background: #fff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px 18px; }
  .tag { background:#dbeafe; color:#1d4ed8; padding:1px 8px; border-radius:10px; font-size:15px; }
  .tag.gold { background:#fef3c7; color:#b45309; }
---

# Solution 5.2 — Xin ý kiến Thầy

## LLM + *System Prompt* điều chỉnh hành vi/kết quả (có Few-shot)

**Đề tài:** Hệ thống tư vấn chọn BĐS thông minh tại TP.HCM
**Mục đích slide:** Trình bày ngắn gọn giải pháp 5.2 để nhờ Thầy đánh giá mức độ phù hợp với môn *DSS with Data*.

> **Ý tưởng chính:** LLM chỉ đóng vai trò *hiểu nhu cầu + giải thích*; mọi quyết định **chấm điểm & xếp hạng** do inference engine làm — đảm bảo kết quả **minh bạch, kiểm chứng được**.

---

# 1. Ý tưởng & vai trò của LLM

<div class="cols">
<div class="card">

### LLM làm gì
<span class="tag">Parser + Giải thích</span>

- Đọc **nhu cầu tự do** tiếng Việt → tách thành `hard_constraints` và `soft_preferences`
- Sinh **lời giải thích** dựa trên điểm/attribute thật

</div>
<div class="card">

### LLM KHÔNG làm gì
<span class="tag gold">Không tự chấm điểm</span>

- Không quyết định ranking
- Không bịa điểm số
- → Phần này do **inference engine** (deterministic)

</div>
</div>

**Cách kiểm soát LLM:** dùng **System Prompt** để định nghĩa vai trò, luật và schema đầu ra; dùng **Few-shot** để cho ví dụ khuôn mẫu khi cần → LLM hoạt động **nhất quán, đoán trước được**.

---

# 2. Pipeline xử lý

```
Form (ràng buộc cứng + trọng số)  +  Free-text (nhu cầu tự do)
        │
        ▼
┌─────────────────────────────────────────┐
│ LLM Parse Intent   [system prompt + few-shot + temp=0]
│   → hard_constraints   (ví dụ: price ≤ 8B, bedrooms ≥ 3)
│   → soft_preferences   (ví dụ: gần trường → nearest_school_m)
└─────────────────────────────────────────┘
        │
        ▼
   Amenity Mapping  ──►  Rule-based Filter → Top 10
        │
        ▼
   POI Enrichment  (khoảng cách thực via Haversine / Map API)
        │
        ▼
   Re-scoring / Re-ranking   ← deterministic, có trọng số
        │
        ▼
   Top 5  ──►  LLM Explanation  [chỉ dựa trên điểm/attribute]
```

---

# 3. Kiểm soát LLM bằng System Prompt + Few-shot

**System Prompt** khóa:
- **Vai trò:** "Real-estate intent parser" — chỉ parse, không chấm điểm
- **Schema đầu ra** cố định (JSON): `hard_constraints`, `soft_preferences`, `unsupported`
- **Whitelist** amenity: chỉ nhận `school / park / hospital / supermarket / main_road`
- **Temperature = 0** → cùng input, cùng output

**Few-shot (ví dụ khuôn mẫu, thêm khi cần):**
```json
User: "Có con nhỏ, muốn gần trường và công viên yên tĩnh"
→ {
  "hard_constraints": [],
  "soft_preferences": [
    {"user_phrase": "gần trường", "amenity": "school",
     "metric": "nearest_school_m", "direction": "lower_better",
     "weight_delta": 0.20, "supported": true},
    {"user_phrase": "yên tĩnh", "amenity": "main_road",
     "metric": "nearest_main_road_m", "direction": "higher_better",
     "weight_delta": 0.10, "supported": true}
  ]
}
```

→ LLM **không tự do sinh kết quả**: hành vi & format bị giới hạn bởi prompt + ví dụ.

---

# 4. Nhờ Thầy đánh giá

**Ba câu hỏi cụ thể:**

1. Cách tách vai trò — **LLM parse + giải thích**, **inference engine chấm điểm/xếp hạng** — có phù hợp tinh thần môn *DSS with Data* không?
2. Việc điều khiển LLM bằng **system prompt + few-shot** (khóa schema, whitelist, temp=0) để đảm bảo kết quả nhất quán — có được chấp nhận là **kiểm chứng đủ** không?
3. **Scope demo** hiện tại (37 BĐS Quận Gò Vấp, output Top 5 + giải thích) — có đủ cho yêu cầu môn học, hay cần mở rộng dataset?

> Cảm ơn Thầy. Nhóm rất mong nhận được góp ý để chốt hướng triển khai.
