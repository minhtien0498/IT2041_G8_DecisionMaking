---
marp: true
title: "Hệ thống tư vấn chọn bất động sản thông minh"
author: "Nhóm 8 — IT2041"
paginate: true
html: true
math: katex
backgroundColor: "#ffffff"
color: "#1d2b36"
# ============================================================
#  MARP TEMPLATE — theme UIT navy (primary #1F3A68), gradient style
#  Quy ước dùng:
#   - Mỗi slide ngăn nhau bằng `---`
#   - Tiêu đề frame nội dung   ->  `## ...`  (ra THANH NAVY gradient tràn viền)
#   - Slide bìa / cảm ơn       ->  thêm `<!-- _class: lead -->`
#   - Slide chuyển mục (section)->  thêm `<!-- _class: divider -->` (nền navy + số mờ lớn)
#   - Footer (tên · đề tài · ngày) sửa ở dòng `footer:` cuối frontmatter
#   - Công thức: KaTeX  $...$ / $$...$$    |  Hình: ![w:600px](path)
#  Components có sẵn: .box .warn .grid2 .cols .flow .chips .mono .pipeline .pill .diagram
# ============================================================
style: |
  @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');
  :root {
    --navy:#1F3A68; --navy-deep:#16294d; --ink:#1d2b36;
    --accent:#2a6df4; --soft:#eef3fb; --line:#d4deee; --muted:#6b7a90;
  }
  section {
    font-family: "Be Vietnam Pro", "Segoe UI", system-ui, sans-serif;
    font-size: 24px;
    padding: 96px 70px 60px 70px;
    background:
      radial-gradient(1200px 380px at 88% -8%, #eef3fb 0%, rgba(238,243,251,0) 60%),
      #ffffff;
    color: var(--ink);
    display: flex; flex-direction: column;
    justify-content: flex-start !important; align-content: flex-start;
    letter-spacing:.1px;
  }
  /* --- THANH HEADER NAVY gradient tràn viền (dùng cho ## slide nội dung) --- */
  h2 {
    position: absolute; top: 0; left: 0; right: 0; margin: 0;
    background: linear-gradient(100deg, var(--navy-deep) 0%, var(--navy) 58%, #28508f 100%);
    color: #ffffff !important; font-size: 29px; font-weight: 600;
    padding: 18px 70px 16px 70px;
    box-shadow: 0 3px 14px rgba(15,29,56,.18);
  }
  h3 {
    color: var(--navy); font-size: 23px; font-weight: 700; margin: 2px 0 14px 0;
    padding-bottom: 7px; border-bottom: 2px solid var(--line); display: inline-block;
  }
  p { margin: 9px 0; }
  strong { color: var(--navy); font-weight: 700; }
  em { color: var(--accent); font-style: normal; font-weight: 600; }
  a { color: var(--navy); }
  code { background: var(--soft); color: var(--navy); padding: 1px 7px; border-radius: 5px; font-size: .94em; }
  /* --- bullet markers gradient vuông bo --- */
  ul { list-style: none; padding-left: 4px; margin: 8px 0; }
  ul li { position: relative; padding-left: 26px; margin: 12px 0; line-height: 1.45; }
  ul li::before {
    content: ""; position: absolute; left: 3px; top: .55em;
    width: 8px; height: 8px; border-radius: 3px;
    background: linear-gradient(135deg, var(--navy), var(--accent));
  }
  ol { padding-left: 22px; } ol li { margin: 11px 0; line-height: 1.45; }
  /* --- bảng bo góc + đổ bóng + zebra --- */
  table { font-size: 21px; border-collapse: collapse; margin: 10px 0; width: 100%;
    box-shadow: 0 2px 10px rgba(15,29,56,.07); border-radius: 10px; overflow: hidden; }
  thead th { background: var(--navy); color: #fff; font-weight: 600; }
  tbody tr:nth-child(even) td { background: #f6f9fe; }
  td, th { border: 1px solid var(--line); padding: 8px 14px; }
  blockquote {
    border: none; border-left: 5px solid var(--accent);
    background: var(--soft); color: #20324f; padding: 12px 22px;
    border-radius: 0 12px 12px 0; margin: 12px 0;
  }
  /* --- công thức display dạng card --- */
  .katex-display {
    background: linear-gradient(180deg, #f7faff 0%, #eef3fb 100%);
    border: 1px solid var(--line); border-left: 5px solid var(--navy);
    border-radius: 12px; padding: 16px 22px; margin: 14px 0;
    box-shadow: 0 2px 12px rgba(15,29,56,.07);
  }
  .katex { font-size: 1.18em; }
  /* --- code block dạng card --- */
  pre { background: #f7faff; border: 1px solid var(--line);
    border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 12px rgba(15,29,56,.06); }
  pre code { background: none; color: #20324f; font-size: 19px; line-height: 1.6; }
  /* --- footer 4 ô gradient (Name | Title | Date | page) --- */
  footer { left:0; bottom:0; width:100%; box-sizing:border-box; display:flex; padding:0;
    height:26px; font-size:13px; color:#ffffff;
    background: linear-gradient(90deg,#0e1d38 0%,#16294d 30%,#1f3a68 62%,#2a4d86 100%); }
  footer span { flex:1; display:flex; align-items:center; justify-content:center;
    border-right:1px solid rgba(255,255,255,.28); }
  footer span:nth-child(4) { flex:0 0 64px; }   /* ô số trang hẹp hơn */
  footer span:last-child { border-right:none; }
  section::after { position:absolute; right:20px; bottom:5px; z-index:10; color:#ffffff;
    font-weight:600; font-size:13px;
    content: attr(data-marpit-pagination) " / " attr(data-marpit-pagination-total); }
  /* --- logo UIT góc phải, hiện trên MỌI slide (qua directive header:) --- */
  header { position:absolute; top:9px; right:16px; left:auto; margin:0; padding:0;
    background:none; box-shadow:none; z-index:40; }
  header img { height:52px; width:52px; object-fit:contain; display:block; background:#ffffff;
    border-radius:50%; padding:6px; box-sizing:border-box; box-shadow:0 1px 5px rgba(0,0,0,.22); }
  section.cover header img { background:none; box-shadow:none; padding:0; }
  /* --- slide bìa / chuyển mục dạng lead --- */
  section.lead { text-align:center; justify-content:center; }
  section.lead::before { content:""; position:absolute; top:0; left:0; right:0; height:8px;
    background: linear-gradient(90deg, var(--navy) 0%, var(--accent) 100%); }
  .titlebox { width:100%; box-sizing:border-box;
    background: linear-gradient(120deg, #16294d 0%, #1F3A68 60%, #2a558f 100%);
    border-radius:16px; padding:30px 44px; margin:10px 0 26px 0;
    box-shadow:0 10px 30px rgba(15,29,56,.22); text-align:center; }
  .titlebox h1 { background:none; border:none; color:#fff !important;
    font-size:42px; margin:0; padding:0; letter-spacing:.3px; }
  .titlebox h3 { color:#cfe0ff !important; font-weight:400; border:none; margin:10px 0 0 0; display:block; }
  section.lead h1 { color:var(--navy); font-size:42px; }
  section.lead h3 { color:var(--ink); font-weight:400; border:none; display:block; }
  .thanks h1 { background:none; border:none; box-shadow:none; color:var(--navy) !important;
    font-size:46px; font-weight:700; margin:40px 0 24px 0; padding:0; }
  /* --- slide chuyển mục (section divider): nền navy + số mờ lớn --- */
  section.divider {
    background-color:#16294d !important;
    background-image: linear-gradient(135deg,#0e1d38 0%,#16294d 45%,#1F3A68 100%) !important;
    color:#eaf1fc; justify-content:center !important; align-content:center;
    padding:96px 80px; overflow:hidden;
  }
  section.divider .dnum { position:absolute; top:14px; right:50px;
    font-size:260px; font-weight:800; line-height:1;
    color:rgba(255,255,255,.06); letter-spacing:-6px; z-index:0; pointer-events:none; }
  section.divider .dbar { width:64px; height:6px; border-radius:3px; position:relative; z-index:1;
    background:linear-gradient(90deg,var(--accent),#86b4ff); margin:0 0 20px 0; }
  section.divider h1 { color:#ffffff !important; background:none; border:none; box-shadow:none;
    font-size:48px; line-height:1.12; margin:0 0 16px 0; padding:0; position:relative; z-index:1; max-width:80%; }
  section.divider .dsub { color:#cfe0ff; font-size:23px; line-height:1.5; max-width:80%; position:relative; z-index:1; }
  section.divider .dmeta { color:#9db4d8; font-size:18px; margin-top:30px; position:relative; z-index:1; }
  /* --- components --- */
  .small { font-size:18px; color:var(--muted); }
  .caption { font-size:16px; color:#888; font-style:italic; }
  .box { background:#f7faff; border:1px solid var(--line); border-left:5px solid var(--accent);
    border-radius:0 12px 12px 0; padding:13px 22px; box-shadow:0 2px 12px rgba(15,29,56,.06); }
  .warn { background:#fff8ec; border:1px solid #f3dca6; border-left:5px solid #e0a51e;
    border-radius:0 12px 12px 0; padding:13px 22px; }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:20px; align-items:start; }
  .cols { display:flex; gap:30px; } .col { flex:1; }
  .center { text-align:center; }
  .yes { color:#15803d; font-weight:700; } .no { color:#b04a4a; font-weight:700; }
  /* flow dọc các bước */
  .flow { display:flex; flex-direction:column; align-items:center; gap:5px; margin:14px 0; }
  .flow .step { background:#fff; border:1.5px solid #cdd9ec; border-radius:10px;
    padding:9px 22px; font-weight:600; color:var(--navy); font-size:21px; box-shadow:0 2px 8px rgba(15,29,56,.06); }
  .flow .step.fill { background:var(--navy); color:#fff; border-color:var(--navy); }
  .flow .ar { color:var(--accent); font-size:17px; line-height:1; }
  /* chips timeline ngang */
  .chips { display:flex; flex-wrap:wrap; align-items:center; gap:7px; justify-content:center; margin:8px 0 4px; }
  .chip { background:var(--navy); color:#fff; border-radius:999px; padding:6px 15px; font-size:18px; font-weight:600; }
  .chip.alt { background:#eef3fb; color:var(--navy); border:1px solid #cdd9ec; }
  .chip.hot { background:linear-gradient(135deg,var(--navy),var(--accent)); }
  .sep { color:#9bb0cf; font-weight:700; }
  /* minh hoạ mono (ma trận/sơ đồ chữ) */
  .mono { background:#0f1f3d; color:#dbe7ff; border-radius:12px; padding:16px 22px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size:19px; line-height:1.55; box-shadow:0 4px 16px rgba(15,29,56,.22); display:inline-block; }
  .mono .dim { color:#7f93bd; }
  /* pipeline / pill */
  .pipeline { background:#f7faff; border:1px solid var(--line); border-radius:12px;
    padding:12px 16px; box-shadow:0 2px 12px rgba(15,29,56,.06);
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size:20px; line-height:1.65; color:#20324f; }
  .pill { display:inline-block; border:1px solid #cdd9ec; background:#fff; color:var(--navy);
    border-radius:999px; padding:3px 12px; margin:3px 4px 3px 0; font-size:18px; }
  /* sơ đồ (ảnh SVG pre-render từ Mermaid) */
  .diagram { text-align:center; margin-top:12px; }
  .diagram img { max-height:300px; width:auto; }
  /* khoảng cách dọc giữa các block component (tránh dính nhau) */
  .box, .warn, .pipeline, .grid2, .cols, pre, table { margin-top:16px; margin-bottom:16px; }
  .mono { margin:8px 0; }
  /* tiện ích thu nhỏ bảng/list khi slide dày */
  .tight table { font-size:18.5px; } .tight li { font-size:22px; }
footer: '<span>Nhóm 8 · IT2041</span><span>Hệ thống tư vấn BĐS thông minh TP.HCM</span><span>Tháng 7, 2026</span><span></span>'
header: '<img src="assets/UIT_logo.svg" alt="UIT">'

---

<!-- _class: lead cover -->
<!-- _paginate: false -->

<div class="titlebox">

# Hệ thống tư vấn chọn bất động sản thông minh
### Ứng dụng DSS with Data cho thị trường nhà ở TP.HCM

</div>

**Nhóm 8 — IT2041**
Trần Tú Quang · Tô Huỳnh Minh Tiến · Nguyễn Ấn · Nguyễn Văn Phú

<br>

<span class="small">University of Information Technology, VNU-HCM (UIT) · Tháng 7, 2026</span>

---

## Nội dung

1. **Bài toán** ra quyết định chọn bất động sản
2. **Dữ liệu**: thu thập, chuẩn hoá, làm giàu tiện ích
3. **Hai giải pháp**: Solution 1 và Solution 2
4. **Đánh giá**: validation set và rubric chung
5. **So sánh và kết luận**

---

<!-- _class: divider -->

<div class="dnum">1</div>
<div class="dbar"></div>

# Bài toán

<div class="dsub">nhu cầu thật · tiêu chí đa chiều · đánh đổi</div>
<div class="dmeta">Phần 1</div>

---

## Chọn nhà là bài toán ra quyết định đa tiêu chí

<div class="grid2">
<div>

**Khó khăn của người mua**
- Hàng nghìn tin đăng, mô tả không chuẩn hoá
- Các tiêu chí xung đột nhau: giá rẻ, gần trung tâm, diện tích rộng
- Tiện ích xung quanh không có sẵn trong tin đăng

</div>
<div>

**Yêu cầu với hệ thống**
- Loại ứng viên vi phạm ràng buộc cứng
- Cân bằng tiêu chí mềm theo mức ưu tiên
- Giải thích được vì sao đề xuất

</div>
</div>

<div class="box">

Mục tiêu: hệ thống hiểu được nhu cầu người dùng, kể cả khi diễn đạt bằng ngôn ngữ tự nhiên, nhưng vẫn giữ tính minh bạch và kiểm chứng được của một DSS.

</div>

---

## Input và Output

<div class="grid2">
<div>

**Input**

`Form cố định`
- Ngân sách tối đa, số phòng ngủ tối thiểu (ràng buộc cứng)
- Trọng số ưu tiên cho trường học, công viên, siêu thị, bệnh viện, trục đường (tiêu chí mềm)

`Nhu cầu thêm` dạng free-text
- *"phải có chợ trong vòng 1km, ưu tiên gần trường mầm non"*

</div>
<div>

**Output**

- Top 5 bất động sản phù hợp nhất
- Điểm số kèm breakdown từng tiêu chí
- Giải thích bằng tiếng Việt
- Danh sách nhu cầu chưa hỗ trợ, có gắn cờ

<div class="pipeline">
form + free-text → Top 5 + explanation
</div>

</div>
</div>

---

<!-- _class: divider -->

<div class="dnum">2</div>
<div class="dbar"></div>

# Dữ liệu

<div class="dsub">thu thập · chuẩn hoá · làm giàu thông tin</div>
<div class="dmeta">Phần 2</div>

---

## Dataset và làm giàu thông tin

<div class="grid2">
<div>

**Dữ liệu bất động sản**
- 100 listings: 50 Gò Vấp và 50 Tân Bình
- Nguồn: tin đăng thật, thị trường TP.HCM 2025
- Chuẩn hoá schema: `property_id`, giá, diện tích, phòng ngủ, `lat/lon`
- Lọc chất lượng: có toạ độ, giá và diện tích hợp lệ

</div>
<div>

**Làm giàu thông tin tiện ích (POI)**
- Gọi OpenStreetMap Overpass API và Geoapify
- Sinh 2 nhóm đặc trưng cho mỗi bất động sản:
  - `distance_to_nearest_*_m`
  - `near_*_count_1km`
- 7 nhóm tiện ích: trường, công viên, bệnh viện, siêu thị, chợ, cà phê, trục đường

</div>
</div>

<div class="box">

Bước này biến tin đăng thô thành decision matrix chấm điểm được, dùng chung cho cả hai giải pháp.

</div>

---

<!-- _class: divider -->

<div class="dnum">3</div>
<div class="dbar"></div>

# Hai giải pháp

<div class="dsub">LLM-driven · Rule-driven</div>
<div class="dmeta">Phần 3</div>

---

## Hai hướng tiếp cận cho cùng một bài toán

<div class="box">

Cả hai nhận cùng input, trả cùng output contract, chạy trên cùng dataset và cùng validation set. Khác nhau ở **nơi ra quyết định thứ hạng**.

</div>

<div class="grid2">
<div>

**Solution 1** · Sequential 2-LLM

<div class="flow">
<div class="step">LLM #1: Reasoner</div>
<div class="ar">▼</div>
<div class="step">Guardrail</div>
<div class="ar">▼</div>
<div class="step">LLM #2: Explainer</div>
</div>

</div>
<div>

**Solution 2** · Hybrid Form + Free-text

<div class="flow">
<div class="step">Parser</div>
<div class="ar">▼</div>
<div class="step">Rule-based: lọc & chấm điểm</div>
<div class="ar">▼</div>
<div class="step">Explainer</div>
</div>

</div>
</div>

<div class="grid2">
<div><span class="small"><b>LLM</b> chấm điểm và xếp hạng</span></div>
<div><span class="small"><b>Rule-based</b> xếp hạng, parser chỉ dịch nhu cầu</span></div>
</div>

---

<!-- _class: tight -->

## Solution 1: Sequential 2-LLM Pipeline

<div class="grid2">
<div>

**LLM #1: Reasoner**
- Tool-calling giới hạn 5 lượt, không phải agent tự trị
- Tools: `sql_filter` (PostgreSQL), `fetch_nearby_custom`, `get_distance_to_place` (Mapbox)
- Chấm điểm theo rubric và few-shot trong prompt

**Guardrail**
- Lọc grounding, loại thông tin LLM không lấy từ dữ liệu

**LLM #2: Explainer**
- Sinh giải thích tiếng Việt cho Top 5

</div>
<div>

**Hạ tầng**
- OpenRouter, xoay nhiều key và fallback nhiều model
- Short-circuit khi form lọc ra rỗng, không tốn quota
- Degrade `status="error"` thay vì sập cả batch

<div class="box">

Điểm mạnh: hiểu ngôn ngữ tự nhiên tốt, kể cả tiếng Việt không dấu, linh hoạt với mọi loại tiện ích nhờ gọi API thật.

</div>

</div>
</div>

---

## Solution 2: Hybrid Form + Free-text

<div class="box">

Ngôn ngữ tự nhiên không thay thế inference engine, mà mở rộng phạm vi tiêu chí hệ thống hiểu và đo được. Rule-based vẫn là nơi ra quyết định.

</div>

Mỗi mệnh đề free-text được quy về 1 trong 4 nhóm, theo nguyên tắc capability-aware:

<div class="tight">

| Nhóm | Vai trò | Ví dụ |
|---|---|---|
| `hard` | Bắt buộc, dùng để loại ứng viên | *"phải có chợ trong vòng 1km"* |
| `soft` | Ưu tiên, dùng để chấm điểm bổ sung | *"ưu tiên gần trường mầm non"* |
| `duplicates` | Đã có trong form, hợp nhất để không đếm 2 lần | *"gần siêu thị"* |
| `unsupported` | Không đo được, gắn cờ và không chấm | *"hợp phong thủy"* |

</div>

<span class="caption">Chỉ giữ nhu cầu quy đổi được sang <code>amenity name</code> mà tool đo được: <i>"càng nhiều chợ càng tốt"</i> → <code>market</code> → <code>nearby_market_count_within_1000m</code></span>

---

## Solution 2: Pipeline

<div class="diagram">

![w:1120px](diagrams/pipeline.svg)

</div>

<span class="caption">Lấy Top 10 làm vùng đệm trước khi re-rank. Một bất động sản hạng 6 theo form có thể lên hạng 1 sau khi xét nhu cầu thêm, nên cắt Top 5 quá sớm sẽ mất ứng viên tốt.</span>

---

## Solution 2: Re-ranking

<div class="grid2">
<div>

**Enrichment bằng Overpass API**
- Dữ liệu tiện ích thật từ OpenStreetMap, phủ cả 2 quận
- Sinh cùng tập thuộc tính cho cả Top 10 để so sánh đồng nhất
- Cache xuống đĩa nên tái lập được, chạy lại không tốn network

</div>
<div>

**Công thức kết hợp**

$$ \text{final} = \alpha \cdot \text{base} + \beta \cdot \text{additional} $$

<span class="small">$\alpha=0.7$ · $\beta=0.3$ · $\alpha+\beta=1$</span>

- `base` (X): điểm từ form
- `additional` (Y): điểm từ nhu cầu thêm

</div>
</div>

<div class="warn">

Form vẫn chi phối phần lớn quyết định với $\alpha=0.7$, nhu cầu thêm chỉ đóng vai trò tinh chỉnh. Tránh để một câu nói tự do lật đổ toàn bộ tiêu chí đã khai báo.

</div>

---

<!-- _class: divider -->

<div class="dnum">4</div>
<div class="dbar"></div>

# Đánh giá

<div class="dsub">validation set · output contract · rubric</div>
<div class="dmeta">Phần 4</div>

---

## Nền tảng để so sánh công bằng

<div class="grid2">
<div>

**Output contract chung**

Hai solution bắt buộc trả cùng schema:

<div class="pipeline">
case_id · solution_id · status
top5[ rank, property_id,
      total_score,
      hard_constraint_pass ]
explanation_summary
unsupported_requirements
latency_ms
</div>

<span class="small">Được phép thêm field riêng như `base_score` hay `tool_calls_summary`, nhưng không được thiếu field bắt buộc.</span>

</div>
<div>

**Validation set dùng chung: 10 case**

<div class="tight">

| Nhóm case | Mục đích |
|---|---|
| `clear` | Nhu cầu rõ ràng, baseline |
| `ambiguous_free_text` | Nhu cầu mơ hồ |
| `conflict_tradeoff` | Tiêu chí xung đột |
| `unsupported` | Nhu cầu không đo được |

</div>

<span class="small">Cùng 1 dataset và cùng 1 bộ case, nên khác biệt kết quả phản ánh đúng khác biệt giải pháp.</span>

</div>
</div>

---

## Rubric chấm điểm

<div class="grid2">
<div>

**Metric định lượng**

<div class="tight">

| Metric | Ý nghĩa |
|---|---|
| `CSR` | Top 5 có thoả ràng buộc cứng |
| `Precision@5`, `Recall@5` | Độ liên quan của Top 5 |
| `NDCG@5`, `MAP` | Chất lượng thứ hạng |
| `Latency_ms` | Tốc độ |

</div>

</div>
<div>

**Cách chấm nhu cầu `unsupported`**

<div class="tight">

| Tình huống | Kết luận |
|---|---|
| Không đo được, gắn cờ rõ ràng | <span class="yes">Đạt</span> |
| Không đo được nhưng vẫn chấm điểm | <span class="no">Lỗi nặng</span> |
| Đo được nhưng không đưa vào output | <span class="no">Lỗi vừa</span> |

</div>

</div>
</div>

<div class="box">

Hệ thống phải nói rõ giới hạn của mình. Gắn cờ "chưa hỗ trợ" tốt hơn là bịa điểm số cho tiêu chí không đo được.

</div>

---

<!-- _class: tight -->

## Kết quả trên validation set chung

<div class="grid2">
<div>

**Mức đồng thuận Top 5**

<div class="tight">

| Số BĐS trùng | Số case |
|---|---|
| 5/5 (giống hệt) | **5** |
| 4/5 | 2 |
| 3/5 | 2 |
| 1/5 | 1 |

</div>

</div>
<div>

**Solution 2**

<div class="tight">

| Chỉ số | Kết quả |
|---|---|
| Case chạy thành công | 10/10 |
| `hard_constraint_pass` | 50/50 |
| Gắn cờ `unsupported` | 8/10 |

</div>

</div>
</div>

<div class="box">

5 case trùng hoàn toàn đều là case free-text **không thêm tiêu chí đo được**. Hai bên chỉ lệch ở `V1_006`, `V1_007`, `V1_008`, `V1_010`, đúng các case có nhu cầu thêm đo được.

</div>

<span class="caption">Phần nền rule-based của hai solution nhất quán; khác biệt xuất hiện đúng chỗ hai bên xử lý nhu cầu thêm theo cách khác nhau.</span>

---

<!-- _class: divider -->

<div class="dnum">5</div>
<div class="dbar"></div>

# So sánh và kết luận

<div class="dsub">điểm mạnh · hạn chế · hướng đi</div>
<div class="dmeta">Phần 5</div>

---

<!-- _class: tight -->

## Solution 1 và Solution 2

| Tiêu chí | Solution 1 (2-LLM) | Solution 2 (Hybrid) |
|---|---|---|
| Nơi ra quyết định | LLM chấm điểm, xếp hạng | Rule-based xếp hạng |
| Hiểu ngôn ngữ tự nhiên | Tốt, kể cả không dấu | Theo từ khoá, có giới hạn |
| Tính tái lập | Lệch giữa các lần chạy | Cùng input, cùng output |
| Minh bạch điểm số | Khó truy vết | Truy vết từng tiêu chí |
| Chi phí, tốc độ | Tốn quota, chậm | Không tốn LLM |
| Phụ thuộc ngoài | OpenRouter, Mapbox, PostgreSQL | Overpass API (có cache) |

<div class="box">

Hai hướng bổ sung cho nhau: Solution 1 mạnh ở khả năng hiểu, Solution 2 mạnh ở minh bạch và ổn định. Đây là đánh đổi quen thuộc của DSS giữa linh hoạt và giải thích được.

</div>

---

## Hạn chế và hướng phát triển

<div class="grid2">
<div>

**Hạn chế hiện tại**
- Dataset mới ở quy mô 100 listings, 2 quận
- Ground truth của validation set do nhóm tự dựng, chưa có khảo sát người mua thật
- Solution 1 phụ thuộc quota và độ ổn định của model free
- Solution 2 hiểu free-text theo từ khoá nên có giới hạn

</div>
<div>

**Hướng phát triển**
- Mở rộng dữ liệu ra nhiều quận, tăng số listings
- Thu thập nhãn relevance từ người dùng thật để có ground truth khách quan
- Kết hợp hai hướng: LLM dịch nhu cầu, rule-based xếp hạng
- Xây giao diện web và bản đồ trực quan

</div>
</div>

---

<!-- _class: lead -->

<div class="thanks">

# Q&A

### Cảm ơn thầy và các bạn đã lắng nghe

<br>

**Nhóm 8 · IT2041**

</div>
