# Solution Comparison Template

File này là khung để `member-4` tổng hợp kết quả giữa các solution.

## 1. Bảng compare theo case

| case_id | persona | group | solution_1_top1 | solution_2_top1 | csr_s1 | csr_s2 | ndcg5_s1 | ndcg5_s2 | unsupported_note | winner | note |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|
| V1_001 | family_with_children | clear | GV_008 | GV_008 | 1.0 | 1.0 | 0.92 | 0.95 | none | solution_2 | top1 giai thich ro hon |

## 2. Bảng compare chi tiet top5

| case_id | solution_id | rank | property_id | total_score | hard_constraint_pass | reason_tags | unsupported_requirements |
|---|---|---:|---|---:|---|---|---|
| V1_001 | solution_1 | 1 | GV_008 | 0.6558 | true | near_school, near_park | |
| V1_001 | solution_2 | 1 | GV_008 | 0.7590 | true | near_school, near_park, market | |

## 3. Bảng tong hop theo persona

| persona | cases | avg_csr_s1 | avg_csr_s2 | avg_ndcg5_s1 | avg_ndcg5_s2 | winner | note |
|---|---:|---:|---:|---:|---:|---|---|
| family_with_children | 2 | 1.00 | 1.00 | 0.88 | 0.94 | solution_2 | free-text giup hon |
| young_professional | 2 | 1.00 | 1.00 | 0.80 | 0.91 | solution_2 | xu ly amenity moi tot hon |

## 4. Bảng tong hop cuoi

| metric | solution_1 | solution_2 | winner | note |
|---|---:|---:|---|---|
| avg_csr | 1.00 | 1.00 | tie | ca hai giu rang buoc cung |
| avg_precision5 | 0.76 | 0.82 | solution_2 | top5 sat nhu cau hon |
| avg_recall5 | 0.92 | 0.94 | solution_2 | lay du candidate tot hon |
| avg_ndcg5 | 0.92 | 0.95 | solution_2 | ranking hop ly hon |
| map | 0.92 | 0.95 | solution_2 | tong hop ranking tot hon |
| avg_latency_ms | 1800 | 2200 | solution_1 | solution 1 nhanh hon |

## 5. Rule dien bang

- `winner` tung case uu tien theo rubric trong `docs/validation_rubric.md`.
- `note` phai ngan, co ly do cu the.
- Neu `CSR` thua, khong cho win chi vi explanation hay.
- Neu hai solution dung bang, ghi `tie`.

## 6. Ket luan de bao cao

Dung 3 dong cuoi:
- `Best stability:` solution nao on dinh nhat
- `Best free-text handling:` solution nao xu ly nhu cau tu nhien tot nhat
- `Recommended final direction:` solution nao nen dem di bao ve final
