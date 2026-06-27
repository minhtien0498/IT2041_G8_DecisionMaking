---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Giải pháp 1 & 2 · Xin ý kiến Thầy'
footer: 'Nhóm 8 (IT2041_G8) · DSS with Data'
style: |
  section {
    background: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 23px;
    padding: 48px 60px;
  }
  section h1 { color: #1d4ed8; font-size: 38px; margin-bottom: 6px; }
  section h2 { color: #1d4ed8; font-size: 25px; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; margin-top: 4px; }
  section h3 { color: #1d4ed8; font-size: 20px; }
  section header { color: #64748b; font-size: 14px; }
  section footer { color: #94a3b8; font-size: 13px; }
  section strong { color: #0f172a; font-weight: 700; }
  section em { color: #1d4ed8; font-style: italic; font-weight: 600; }
  table { font-size: 17px; border-collapse: collapse; width: 100%; margin-top: 8px; }
  th { background: #1d4ed8; color: #fff; padding: 7px 10px; text-align: left; }
  td { background: #fff; padding: 6px 10px; border-bottom: 1px solid #e2e8f0; }
  code { background: #eef2f7; color: #0f172a; padding: 1px 6px; border-radius: 4px; font-size: 0.9em; }
  pre { background: #f1f5f9; color: #0f172a; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 15px; }
  blockquote { border-left: 3px solid #cbd5e1; background: #f1f5f9; color: #334155; padding: 8px 14px; border-radius: 4px; font-style: normal; }
  .pipe { background:#fff; border:1px solid #cbd5e1; border-radius:8px; padding:14px 20px; font-family:'Consolas',monospace; font-size:16px; }
---

# Giải pháp 1 & 2

## LLM + *System Prompt* điều chỉnh hành vi/kết quả (có Few-shot)

**Đề tài:** Hệ thống tư vấn chọn BĐS thông minh tại TP.HCM
**Mục đích:** Trình bày 2 giải pháp, nhờ Thầy đánh giá mức phù hợp với môn *DSS with Data*.

Cả hai giải pháp đều dùng **LLM kết hợp system prompt** để điều khiển hành vi và kết quả đầu ra (có **few-shot** làm ví dụ khuôn mẫu khi cần). LLM **không tự quyết** — điểm số luôn neo vào dữ liệu.

---

# 1. Nền tảng chung & điểm khác biệt

**Chung cho cả Solution 1 và Solution 2:**
- Input: **form** (ràng buộc cứng + trọng số) + **free-text** (nhu cầu tự do)
- Dùng **system prompt + few-shot** để kiểm soát LLM
- Output: **Top 5 + lời giải thích**

| | Solution 1 | Solution 2 |
|---|---|---|
| *Nơi ra quyết định* | Trong LLM (fuzzy reasoning) | Inference engine (rule-based) |
| *Vai trò LLM* | Suy luận + giải thích | Parse intent + giải thích |
| *Điểm số* | Fuzzy satisfaction theo rubric | Score deterministic |
| *Đặc trưng Top 5* | Đa dạng theo cluster tradeoff | Xếp hạng theo thứ tự |

---

# 2. Solution 1 — Fuzzy LLM Reasoning

**Ý tưởng:** LLM hiểu nhu cầu mơ hồ bằng *fuzzy reasoning*, tìm kiếm nhiều vòng từ nhiều góc độ, gom kết quả thành các cluster tradeoff, chọn Top 5 đa dạng.

<div class="pipe">

Form + Free-text
&nbsp;&nbsp;→ LLM Semantic Fusion
&nbsp;&nbsp;→ Fuzzy Analysis (gắn rubric µ cho từng chiều mờ)
&nbsp;&nbsp;→ Multi-Round Vector Search
&nbsp;&nbsp;→ Result Clustering
&nbsp;&nbsp;→ SQL Hard-Constraint Filter
&nbsp;&nbsp;→ Top 5 đa dạng (cân bằng cluster)
&nbsp;&nbsp;→ LLM Explanation + Tradeoff

</div>

Mỗi điểm số truy được cơ sở, ví dụ `µ_price = 0.9` vì giá 3.6B vượt budget 3.5B đúng 0.1B theo rubric.

---

# 3. Solution 2 — Rule-based Core

**Ý tưởng:** LLM chỉ *parse* nhu cầu tự do thành hard/soft constraint; inference engine làm toàn bộ **chấm điểm & xếp hạng** deterministic. LLM không quyết định ranking.

<div class="pipe">

Form + Free-text
&nbsp;&nbsp;→ LLM Parse Intent (hard / soft constraint)
&nbsp;&nbsp;→ Amenity Mapping
&nbsp;&nbsp;→ Rule-based Filter → Top 10
&nbsp;&nbsp;→ POI Enrichment (khoảng cách thực)
&nbsp;&nbsp;→ Re-scoring / Re-ranking (deterministic)
&nbsp;&nbsp;→ Top 5
&nbsp;&nbsp;→ LLM Explanation

</div>

Điểm được tính bằng công thức cố định (chuẩn hóa + trọng số), kiểm tra lại được từng bước — không phụ thuộc "cảm giác" của LLM.

---

# 4. Cách kiểm soát LLM — System Prompt + Few-shot

**System Prompt** định nghĩa:
- **Vai trò:** LLM chỉ parse intent / giải thích, **không chấm điểm**
- **Schema đầu ra** cố định (JSON): `hard_constraints`, `soft_preferences`
- **Whitelist** amenity: `school / park / hospital / supermarket / main_road`
- **Temperature = 0** → cùng input, cùng output

**Few-shot** — ví dụ khuôn mẫu (thêm khi cần). Cho LLM vài cặp *input → output* để nó theo khuôn mẫu:

```
User: "gần trường, yên tĩnh"
  gần trường  →  school     →  nearest_school_m     (càng gần càng tốt,  +0.20)
  yên tĩnh    →  main_road  →  nearest_main_road_m  (càng xa càng tốt,   +0.10)
```

→ LLM **không tự do sinh kết quả**: hành vi và format bị giới hạn bởi prompt + ví dụ.

---

# 5. Nhờ Thầy đánh giá

1. Việc dùng **LLM + system prompt + few-shot** để kiểm soát hành vi/kết quả (khóa schema, whitelist, `temp=0`) — có đảm bảo **mức kiểm chứng đủ** cho môn học không?
2. Cách tách vai trò giữa hai giải pháp — **Solution 1** (LLM suy luận + rubric µ) vs **Solution 2** (LLM parse, inference engine chấm điểm) — hướng nào phù hợp tinh thần *DSS with Data* hơn?
3. **Scope demo** hiện tại (37 BĐS Quận Gò Vấp, Top 5 + giải thích) — có đủ, hay cần mở rộng dataset?

> Cảm ơn Thầy. Nhóm rất mong góp ý để chốt hướng triển khai.
