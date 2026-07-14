# Solution Comparison Template

File này là khung để `Ấn` tổng hợp kết quả giữa các solution.

Quy ước hiện tại:
- `Solution 2`: hướng của `Quang`
- `Solution 1`: pipeline hai LLM có guardrail của `Phú`
- baseline rule-based cũ chỉ giữ làm historical reference nếu cần nhắc lại

## 1. Bảng compare theo case

| case_id | persona | group | solution_2_top1 | solution_1_top1 | csr_s2 | csr_s3 | ndcg5_s2 | ndcg5_s3 | unsupported_note | winner | note |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|
| V1_001 | family_with_children | clear | GV_008 | GV_008 | 1.0 | 1.0 | 0.92 | 0.95 | none | solution_1 | top1 giai thich ro hon |

## 2. Bảng compare chi tiet top5

| case_id | solution_id | rank | property_id | total_score | hard_constraint_pass | reason_tags | unsupported_requirements |
|---|---|---:|---|---:|---|---|---|
| V1_001 | solution_2 | 1 | GV_008 | 0.6558 | true | near_school, near_park | |
| V1_001 | solution_1 | 1 | GV_008 | 0.7590 | true | near_school, near_park, market | |

## 3. Bảng tong hop theo persona

| persona | cases | avg_csr_s2 | avg_csr_s3 | avg_ndcg5_s2 | avg_ndcg5_s3 | winner | note |
|---|---:|---:|---:|---:|---:|---|---|
| family_with_children | 2 | 1.00 | 1.00 | 0.88 | 0.94 | solution_1 | free-text giup hon |
| young_professional | 2 | 1.00 | 1.00 | 0.80 | 0.91 | solution_2 | xu ly amenity moi tot hon |

## 4. Bảng tong hop cuoi

| metric | solution_2 | solution_1 | winner | note |
|---|---:|---:|---|---|
| avg_csr | 1.00 | 1.00 | tie | ca hai giu rang buoc cung |
| avg_precision5 | 0.76 | 0.82 | solution_1 | top5 sat nhu cau hon |
| avg_recall5 | 0.92 | 0.94 | solution_1 | lay du candidate tot hon |
| avg_ndcg5 | 0.92 | 0.95 | solution_1 | ranking hop ly hon |
| map | 0.92 | 0.95 | solution_1 | tong hop ranking tot hon |
| avg_latency_ms | 2200 | 9000 | solution_2 | solution 2 nhanh hon trong demo neu Solution 1 goi nhieu luot LLM/tool |

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
