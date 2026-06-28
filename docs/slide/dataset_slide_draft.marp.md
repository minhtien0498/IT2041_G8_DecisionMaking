---
marp: true
title: "Dataset Mở Rộng Cho Hệ Thống Tư Vấn Bất Động Sản"
author: "Tiến"
paginate: true
html: true
math: katex
backgroundColor: "#ffffff"
color: "#1d2b36"
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
  code { background: var(--soft); color: var(--navy); padding: 1px 7px; border-radius: 5px; font-size: .94em; }
  ul { list-style: none; padding-left: 4px; margin: 8px 0; }
  ul li { position: relative; padding-left: 26px; margin: 12px 0; line-height: 1.45; }
  ul li::before {
    content: ""; position: absolute; left: 3px; top: .55em;
    width: 8px; height: 8px; border-radius: 3px;
    background: linear-gradient(135deg, var(--navy), var(--accent));
  }
  table { font-size: 20px; border-collapse: collapse; margin: 10px 0; width: 100%;
    box-shadow: 0 2px 10px rgba(15,29,56,.07); border-radius: 10px; overflow: hidden; }
  thead th { background: var(--navy); color: #fff; font-weight: 600; }
  tbody tr:nth-child(even) td { background: #f6f9fe; }
  td, th { border: 1px solid var(--line); padding: 8px 14px; }
  .small { font-size:18px; color:var(--muted); }
  .box { background:#f7faff; border:1px solid var(--line); border-left:5px solid var(--accent);
    border-radius:0 12px 12px 0; padding:13px 22px; box-shadow:0 2px 12px rgba(15,29,56,.06); }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:20px; align-items:start; }
  footer { left:0; bottom:0; width:100%; box-sizing:border-box; display:flex; padding:0;
    height:26px; font-size:13px; color:#ffffff;
    background: linear-gradient(90deg,#0e1d38 0%,#16294d 30%,#1f3a68 62%,#2a4d86 100%); }
  footer span { flex:1; display:flex; align-items:center; justify-content:center;
    border-right:1px solid rgba(255,255,255,.28); }
  footer span:nth-child(4) { flex:0 0 64px; }
  footer span:last-child { border-right:none; }
  section::after { position:absolute; right:20px; bottom:5px; z-index:10; color:#ffffff;
    font-weight:600; font-size:13px;
    content: attr(data-marpit-pagination) " / " attr(data-marpit-pagination-total); }
  section.lead { text-align:center; justify-content:center; }
  .titlebox { width:100%; box-sizing:border-box;
    background: linear-gradient(120deg, #16294d 0%, #1F3A68 60%, #2a558f 100%);
    border-radius:16px; padding:30px 44px; margin:10px 0 26px 0;
    box-shadow:0 10px 30px rgba(15,29,56,.22); text-align:center; }
  .titlebox h1 { background:none; border:none; color:#fff !important;
    font-size:42px; margin:0; padding:0; letter-spacing:.3px; }
  .titlebox h3 { color:#cfe0ff !important; font-weight:400; border:none; margin:10px 0 0 0; display:block; }
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
footer: '<span>Tiến</span><span>Dataset Mở Rộng BĐS</span><span>June 27, 2026</span><span></span>'
---

<!-- _class: lead -->
<!-- _paginate: false -->

<div class="titlebox">

# Dataset Mở Rộng Cho Hệ Thống Tư Vấn Bất Động Sản
### Member-3 · Dataset / Data Overview

</div>

**Tiến**

<br>

<span class="small">Bộ dữ liệu mở rộng 100 căn · Gò Vấp + Tân Bình</span>

---

## Mục tiêu mở rộng dataset

- Tăng quy mô từ bộ dữ liệu nhỏ ban đầu lên **100 căn**.
- Giữ cấu trúc dữ liệu đủ sạch để hai solution cùng dùng.
- Chia đều theo hai quận gần nhau:
  - **50 căn Gò Vấp**
  - **50 căn Tân Bình**
- Tạo nền cho bước enrich POI và validation ở giai đoạn sau.

<div class="box">

**Kết quả hiện tại:** đã tạo xong file `data/go_vap_tan_binh_100.json`.

</div>

---

## Tổng quan dataset 100 căn

| Nguồn | Quy mô | Vai trò |
|---|---:|---|
| `data/go_vap_tan_binh_100.json` | 100 BĐS | Dataset clean mở rộng cho scope final |
| `docs/data_public.csv` | 51,304 dòng | Nguồn gốc để extract |
| `docs/vietnam_housing_dataset.csv` | 30,229 dòng | Nguồn tham khảo mở rộng |

| Chỉ số | Giá trị |
|---|---|
| Giá | 1.25 - 27.0 tỷ, trung bình 8.27 |
| Diện tích | 20.0 - 258.4 m², trung bình 69.1 |
| Phòng ngủ | 1 - 7, trung bình 3.5 |
| Phân bổ quận | Gò Vấp: 50, Tân Bình: 50 |

---

## Schema và chất lượng dữ liệu

<div class="grid2">
<div>

### Cột ổn định

- `property_id`
- `price_million_vnd`
- `area_m2`
- `bedrooms`
- `bathrooms`
- `latitude`
- `longitude`

</div>
<div>

### Cột cần lưu ý

- `floors`: 2/100 null
- `direction`: 75/100 null
- `position`: 14/100 null
- `description_snippet`: 5/100 null
- `distance_to_nearest_*`: 100/100 null

</div>
</div>

<div class="box">

**Kết luận:** bộ 100 căn hiện là **clean dataset**, chưa phải **enriched dataset**.

</div>

---

## Kết luận và bước tiếp theo

- Bộ `100` căn đã đủ tốt để:
  - khóa schema chung
  - làm report/slide dataset
  - chuẩn bị scope final lớn hơn
- Bộ này **chưa đủ** để chạy ranking có POI ngay.
- Bước tiếp theo cần làm:
  - enrich lại các cột `distance_to_nearest_*`
  - sau đó mới dùng cho evaluation đầy đủ

<div class="box">

**Gợi ý dùng ngay:** dùng bộ này cho phần dữ liệu và mô tả schema; dùng bước enrich tiếp theo nếu muốn ranking hoàn chỉnh.

</div>
