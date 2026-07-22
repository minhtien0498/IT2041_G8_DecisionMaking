---
marp: true
title: "Validation và Evaluation"
author: "Ấn"
paginate: true
html: true
math: katex
backgroundColor: "#ffffff"
color: "#1d2b36"
style: |
  section { font-family: "Be Vietnam Pro", "Segoe UI", system-ui, sans-serif; font-size: 24px; padding: 84px 70px 52px 70px; color:#1d2b36; }
  h1, h2 { color:#1F3A68; }
  h2 { position:absolute; top:0; left:0; right:0; margin:0; background:#1F3A68; color:#fff; padding:18px 70px; font-size:30px; }
  table { font-size:20px; border-collapse:collapse; width:100%; }
  th { background:#1F3A68; color:#fff; }
  td, th { border:1px solid #d4deee; padding:8px 12px; }
  .box { background:#f7faff; border-left:5px solid #2a6df4; padding:14px 20px; }
footer: '<span>Ấn</span><span>Validation / Evaluation</span><span>July 15, 2026</span>'
---

<!-- _paginate: false -->

# Validation và Evaluation

### Member-4 · Validation / Comparison

**Ấn**

<div class="box">
Mục tiêu: so sánh Solution 1 và Solution 2 công bằng trên cùng validation set, cùng output contract và cùng rubric.
</div>

---

## Validation Set

| Nhóm | Case | Ý nghĩa |
|---|---|---|
| `X-only` | V1_001 - V1_005 | Chấm theo tiêu chí nền: giá, diện tích, phòng ngủ, POI có sẵn |
| `X + Y` | V1_006, 007, 008, 010, 011, 012, 013 | Free-text có thêm tiêu chí đo được |
| `unsupported` | V1_009 | Nhu cầu chủ quan/chưa có dữ liệu đo |

<div class="box">
Sau cập nhật: 13 validation case, toàn bộ user_need_text đã có dấu để tránh nhập nhằng.
</div>

---

## Vì Sao Phải Chấm Theo X + Y

`X` = tiêu chí nền trong form/dataset  
`Y` = tiêu chí sinh từ free-text và đo được bằng POI/tool

Ví dụ cause-effect:

- User nói: "gần trường mầm non".
- Nếu chấm chỉ theo `X`, hệ thống chỉ nhìn `distance_to_nearest_school_m`.
- Nếu solution tìm được `distance_to_nearest_kindergarten_m`, đó là xử lý đúng `Y`.
- Vì vậy ground truth phải xét `X + Y`, nếu không sẽ phạt sai solution xử lý free-text tốt.

---

## Compare Hiện Tại

| Metric | Value |
|---|---:|
| Common cases | 10 |
| S1 Mapbox coverage | 10/10 |
| S2 coverage | 13/13 |
| Same Top 1 | 4/10 |
| Average Top5 overlap | 2.50/5 |

<div class="box">
S1 đã có Mapbox 10 case. S2 đã có đủ 13 case. Final vẫn chờ S1 chạy V1_011-V1_013.
</div>

---

## Case Cần Manual Review

| Case | Solution 2 Top1 | Solution 1 Mapbox Top1 | Vì sao cần review |
|---|---|---|---|
| V1_008 | TB_035 | GV_037 | User cần nhiều chợ; phải xét Y = market count |
| V1_010 | GV_010 | GV_002 | User cần cafe + đường lớn, nhưng yên tĩnh unsupported |

Kết luận tạm:

- Case thường: hai solution khá đồng nhất.
- Case free-text đo được: cần xem solution nào giải thích rõ tác động của `Y`.

---

## Provider Sensitivity - Solution 1

| Metric | Value |
|---|---:|
| Same Top 1 cả 3 provider | 2/10 |
| M-G Top5 overlap | 2.30/5 |
| M-O Top5 overlap | 2.00/5 |
| G-O Top5 overlap | 3.20/5 |

<div class="box">
Provider đổi -> POI distance/count đổi -> ranking đổi. Validation final phải ghi rõ provider.
</div>

---

## Trạng Thái Bàn Giao

Đã xong phần độc lập của Ấn:

- Validation set 13 case
- Rubric `X-only / X + Y / unsupported`
- Compare template Solution 1 vs Solution 2
- Compare hiện tại S1 Mapbox vs S2
- Report draft validation + provider sensitivity

Còn chờ:

- Phú đã có Mapbox/Geoapify/Overpass 10 case; còn S1 V1_011-V1_013
- Quang đã có Solution 2 đủ 13 case
- Sau đó cập nhật compare final và kết luận winner
