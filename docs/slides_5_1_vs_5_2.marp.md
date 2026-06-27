---
marp: true
theme: default
paginate: true
size: 16:9
math: katex
header: 'Hệ thống tư vấn BĐS thông minh · Solution 5.1 vs 5.2'
footer: 'Nhóm 8 (IT2041_G8) · DSS with Data'
style: |
  section {
    background: #f8fafc;
    color: #0f172a;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 23px;
    padding: 50px 60px;
  }
  section h1 {
    color: #1d4ed8;
    font-size: 40px;
    margin-bottom: 6px;
  }
  section h2 {
    color: #b45309;
    font-size: 28px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 4px;
  }
  section h3 { color: #1d4ed8; font-size: 22px; }
  section header { color: #64748b; font-size: 14px; }
  section footer { color: #94a3b8; font-size: 13px; }
  section strong { color: #b45309; }
  section em { color: #1d4ed8; font-style: normal; font-weight: 600; }
  table {
    font-size: 18px;
    border-collapse: collapse;
    width: 100%;
    margin-top: 10px;
  }
  th { background: #1d4ed8; color: #fff; padding: 8px 10px; text-align: left; }
  td { background: #fff; padding: 7px 10px; border-bottom: 1px solid #e2e8f0; }
  code {
    background: #e2e8f0;
    color: #b45309;
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.9em;
  }
  pre { background: #0f172a; color: #e2e8f0; border-radius: 8px; font-size: 16px; }
  blockquote {
    border-left: 4px solid #b45309;
    background: #fffbeb;
    color: #78350f;
    padding: 10px 16px;
    border-radius: 4px;
    font-style: normal;
  }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
  .card { background: #fff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px 18px; }
  .card h3 { margin-top: 0; }
  .tag { background:#dbeafe; color:#1d4ed8; padding:1px 8px; border-radius:10px; font-size:15px; }
  .tag.gold { background:#fef3c7; color:#b45309; }
---

# Solution 5.1 vs 5.2 — Phiên bản mới

## LLM "tự quyết" hay **dựa trên giá trị**?

Hệ thống tư vấn BĐS thông minh · DSS with Data
Nhóm 8 — IT2041_G8

> Cả hai solution đều dùng LLM, nhưng **LLM không bao giờ tự do bịa điểm**. Slide này giải thích cơ chế neo điểm số vào dữ liệu thật.

---

# 1. Hai solution mới — cùng input, khác *nơi ra quyết định*

<div class="cols">
<div class="card">

### Solution 5.1 — *LLM làm bộ suy luận*
<span class="tag">Fuzzy reasoning</span>

- Input: **form + free-text** → LLM gộp thành 1 mô tả ngữ nghĩa
- Quyết định diễn ra **bên trong LLM**: fuzzy analysis, multi-round search, clustering
- Điểm: **fuzzy satisfaction [0,1]** theo rubric
- Top 5: **đa dạng** từ nhiều cluster tradeoff

</div>
<div class="card">

### Solution 5.2 — *Inference engine làm lõi*
<span class="tag gold">Rule-based core</span>

- Input: **form + free-text** → LLM parse thành hard/soft constraint
- Quyết định nằm ở **inference engine**: lọc + chấm + xếp hạng deterministic
- Điểm: **score tuyến tính** từ normalization + weights
- Top 5: xếp hạng theo thứ tự

</div>
</div>

**Câu hỏi chung mà thầy sẽ đặt:** *"Điểm số lấy từ đâu? LLM có tự bịa không?"* → Trả lời ở các slide sau.

---

# 2. Câu hỏi then chốt: LLM có "tự quyết" không?

<div class="cols">
<div>

### Nỗi lo (hợp lý)
Nếu để LLM tự trả `"quality": 0.97`, `"price": 0.55`… thì đó chỉ là **con số bịa**, không kiểm chứng được → mâu thuẫn tinh thần DSS *with Data*.

</div>
<div>

### Câu trả lời của nhóm
Điểm số **không tự do sinh ra**. Nó bị **neo vào 3 lớp**, và mỗi lớp đều **dựa trên giá trị dữ liệu**:

1. **Hard constraints** (SQL) — cutoff tuyệt đối
2. **Rubric trong system prompt** — đường cong chấm điểm = *membership function*
3. **Few-shot + temperature = 0** — khóa tính nhất quán

</div>
</div>

> LLM chỉ là **người áp dụng rubric**, không phải **người sáng tạo điểm**.

---

# 3. Ba lớp neo quyết định vào dữ liệu

| Lớp | Cơ chế | Mức tự do của LLM |
|---|---|---|
| **1. Hard constraint** | `WHERE bedrooms=3 AND price <= 3.5B` (SQL filter) | ❌ Không có — loại tuyệt đối |
| **2. Rubric (system prompt)** | Đường cong điểm cho từng chiều mờ (giá, vị trí, tiện ích) | Rất hẹp — chỉ áp dụng công thức cho trước |
| **3. Few-shot + temp=0** | Vài ví dụ input→score + nhiệt độ 0 | Cố định — cùng input → cùng output |

**Kết quả:** LLM **không thể** cho giá 3.6B điểm 9 với property này rồi điểm 7 với property kia cùng giá — rubric bắt buộc nhất quán.

---

# 4. Lớp 2 — Rubric *chính là* một membership function

**Ví dụ chiều "giá hợp lý"** — ngân sách tham chiếu = **3.5 tỷ**:

| Giá BĐS | `µ_price` | Điểm /10 | Diễn giải |
|---|---|---|---|
| **3.5B** (= budget) | **1.00** | **10** | Hoàn toàn thỏa mãn |
| 3.6B (+0.1B) | 0.90 | 9 | Vượt nhẹ, trừ 1 điểm |
| 3.7B (+0.2B) | 0.80 | 8 | Trừ thêm 1 điểm |
| 3.8B (+0.3B) | 0.70 | 7 | … |
| 4.5B (+1.0B) | 0.00 | 0 | Hoàn toàn ngoài tầm |

> Mỗi **+0.1 tỷ** so với ngân sách → trừ **1 điểm**. Đây **không phải ý kiến** của LLM — nó là **đường cong định sẵn** trong system prompt.

---

# 5. Từ rubric → công thức fuzzy (µ_price)

<div class="cols">
<div>

### Rubric rời rạc (system prompt)
```
budget = 3.5B
tolerance = 1.0B   # cửa sổ dung sai
step = 0.1B        # mỗi bước trừ 1 điểm
```

### Công thức tương đương
$$\mu_{price}(p) = \max\!\left(0,\; 1 - \frac{p - \text{budget}}{\text{tolerance}}\right)$$

</div>
<div>

### Ý nghĩa cho môn DSS
- Rubric trong system prompt **chính là** một **hàm thuộc (membership function)** của fuzzy logic — chỉ là dạng *rời rạc* thay vì liên tục.
- → "Fuzzy satisfaction [0,1]" trong 5.1 là **fuzzy thật**, có cơ sở toán học, **kiểm tra được**.
- Cùng nguyên lý áp dụng cho các chiều khác: `µ_location`, `µ_amenity`, `µ_quietness`…

</div>
</div>

> Nếu cần độ chính xác tuyệt đối, nhóm có thể **tính µ bằng code** và để LLM **chỉ giải thích** — đó là dạng 5.2. Ở 5.1, LLM áp dụng rubric để giữ tính linh hoạt với nhu cầu tự do.

---

# 6. Solution 5.1 — Pipeline

```
Form + Free-Text
  → LLM Semantic Fusion          (gộp thành 1 mô tả ngữ nghĩa)
  → Fuzzy Analysis               (gắn rubric µ cho từng chiều mờ)
  → Multi-Round Vector Search    (nhiều diễn giải, nhiều vòng)
  → Result Clustering            (nhóm theo tradeoff)
  → SQL Hard-Constraint Filter   (cắt tuyệt đối)
  → Top 5 đa dạng (cân bằng cluster)
  → LLM Explanation + Tradeoff
```

**Mỗi điểm số trong output đều truy được:** `µ_price=0.9 vì giá 3.6B > budget 3.5B đúng 0.1B theo rubric`.

---

# 7. Solution 5.2 — Pipeline

```
Form + Free-Text
  → LLM Parse Intent             (tách hard / soft constraint)
  → Amenity Mapping              (map "gần trường" → nearest_school_m)
  → Rule-based Filtering → Top 10
  → Tool-based POI Enrichment    (Mapbox / Google / OSM)
  → Re-scoring / Re-ranking      (deterministic, weights từ form)
  → Top 5
  → LLM Explanation
```

**LLM chỉ làm 2 việc:** (1) *parse* intent thành tham số, (2) *viết* giải thích. Toàn bộ **điểm + xếp hạng** do inference engine tính.

---

# 8. So sánh & định vị

| Tiêu chí | 5.1 (Fuzzy LLM) | 5.2 (Rule-based core) |
|---|---|---|
| Nơi ra quyết định | Trong LLM (có rubric) | Inference engine |
| Xử lý nhu cầu mơ hồ | ✅ Rất mạnh | ⚠️ Giới hạn POI đã map |
| Tính minh bạch | Rubric µ (kiểm tra được) | ✅ Tuyệt đối, deterministic |
| Độ ổn định (reproducibility) | Tốt nếu temp=0 + few-shot | ✅ Hoàn toàn |
| Chi phí / độ trễ | Cao (nhiều vòng search) | Trung bình |
| Validate (NDCG@5, MAP@5) | Khó hơn | ✅ Dễ |

**Điểm chung quan trọng:** cả hai **không để LLM tự quyết** — đều neo vào hard constraint + hàm điểm có cơ sở (rubric µ / normalization).

---

# 9. Kết luận

> **Điểm số do LLM sinh ra, nhưng KHÔNG tùy tiện** — đó là kết quả áp dụng một **membership function có thể kiểm tra**, định nghĩa sẵn trong *system prompt* + *few-shot*.

- **5.1**: linh hoạt, xử lý nhu cầu mờ, Top 5 đa dạng tradeoff — phù hợp khi người dùng mô tả tự do.
- **5.2**: minh bạch tuyệt đối, deterministic, dễ validate — phù hợp làm mốc so sánh và demo ổn định.
- **Hai solution bổ sung cho nhau**, cùng tinh thần DSS *with Data*: quyết định **dựa trên giá trị**, LLM chỉ **hỗ trợ suy luận và giải thích**.
