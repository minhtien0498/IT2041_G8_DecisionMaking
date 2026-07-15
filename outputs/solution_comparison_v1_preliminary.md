# Preliminary Solution Comparison V1

Generated for `Ấn` on 2026-07-15. This compares only cases that already have outputs from both solutions.

## Summary

- Compared cases: 10
- Missing after validation expansion: V1_011, V1_012, V1_013
- Same Top 1: 8/10
- Average Top5 overlap: 4.00/5
- Avg latency Solution 2: 15559.8 ms
- Avg latency Solution 1: 239221.0 ms

## Case Compare

| case_id | persona | group | scope | solution_2_top1 | solution_1_top1 | top5_overlap | winner | note |
|---|---|---|---|---|---|---:|---|---|
| V1_001 | family_with_children | clear | X-only | GV_010 | GV_010 | 5 | tie | same top1 |
| V1_002 | young_professional | clear | X-only | GV_002 | GV_002 | 5 | tie | same top1 |
| V1_003 | investor | clear | X-only | GV_010 | GV_010 | 3 | tie | same top1 |
| V1_004 | elderly | clear | X-only | GV_009 | GV_009 | 5 | tie | same top1 |
| V1_005 | couple | clear | X-only | GV_002 | GV_002 | 5 | tie | same top1 |
| V1_006 | family_with_children | ambiguous_free_text | X+Y | GV_008 | GV_008 | 3 | tie | same top1 |
| V1_007 | young_professional | ambiguous_free_text | X+Y | GV_002 | GV_002 | 1 | tie | same top1 |
| V1_008 | investor | conflict_tradeoff | X+Y | TB_035 | GV_010 | 4 | manual_review | different top1; inspect Y/explanation |
| V1_009 | elderly | unsupported | unsupported | GV_009 | GV_009 | 5 | tie | same top1 |
| V1_010 | couple | conflict_tradeoff | X+Y | GV_010 | GV_002 | 4 | manual_review | different top1; inspect Y/explanation |

## Top5 Detail

| case_id | solution_id | rank | property_id | total_score | hard_constraint_pass | reason_tags | unsupported_requirements |
|---|---|---:|---|---:|---|---|---|
| V1_001 | solution_2 | 1 | GV_010 | 0.6558 | True | good_price, near_school, near_park, near_supermarket | Gia dinh co 2 con nho |
| V1_001 | solution_2 | 2 | GV_008 | 0.6322 | True | good_price, near_school | Gia dinh co 2 con nho |
| V1_001 | solution_2 | 3 | GV_013 | 0.6261 | True | good_price, near_school, near_park, near_supermarket | Gia dinh co 2 con nho |
| V1_001 | solution_2 | 4 | GV_015 | 0.6222 | True | good_price, near_school, near_park, near_supermarket | Gia dinh co 2 con nho |
| V1_001 | solution_2 | 5 | GV_026 | 0.5661 | True | near_school, near_park, near_supermarket | Gia dinh co 2 con nho |
| V1_001 | solution_1 | 1 | GV_010 | 0.66 | True | Giá tốt, Gần trường học, Gần công viên, Gần siêu thị, Diện tích khá |  |
| V1_001 | solution_1 | 2 | GV_008 | 0.63 | True | Giá rất tốt, Rất gần trường học, Gần công viên, Gần siêu thị |  |
| V1_001 | solution_1 | 3 | GV_013 | 0.63 | True | Giá tốt, Gần trường học, Rất gần công viên, Gần siêu thị, 4 phòng ngủ |  |
| V1_001 | solution_1 | 4 | GV_015 | 0.62 | True | Giá tốt, Gần trường học, Gần công viên, Rất gần siêu thị |  |
| V1_001 | solution_1 | 5 | GV_026 | 0.57 | True | Gần trường học, Gần công viên, Gần siêu thị, Diện tích tốt |  |
| V1_002 | solution_2 | 1 | GV_002 | 0.638 | True | good_price, near_supermarket, near_boulevard | Muon gia re |
| V1_002 | solution_2 | 2 | GV_010 | 0.5413 | True | near_supermarket, near_boulevard | Muon gia re |
| V1_002 | solution_2 | 3 | GV_011 | 0.4967 | True | near_supermarket, near_boulevard | Muon gia re |
| V1_002 | solution_2 | 4 | GV_003 | 0.4662 | True | good_price, near_boulevard | Muon gia re |
| V1_002 | solution_2 | 5 | GV_015 | 0.4551 | True | near_supermarket | Muon gia re |
| V1_002 | solution_1 | 1 | GV_002 | 0.638 | True | Giá tốt, Gần siêu thị, Gần trục đường lớn |  |
| V1_002 | solution_1 | 2 | GV_010 | 0.5413 | True | Gần siêu thị, Gần trục đường lớn, Diện tích rộng, Số phòng ngủ tốt |  |
| V1_002 | solution_1 | 3 | GV_011 | 0.4967 | True | Gần siêu thị, Gần trục đường lớn |  |
| V1_002 | solution_1 | 4 | GV_003 | 0.4662 | True | Giá tốt, Gần trục đường lớn |  |
| V1_002 | solution_1 | 5 | GV_015 | 0.4551 | True | Gần siêu thị, Diện tích tốt |  |
| V1_003 | solution_2 | 1 | GV_010 | 0.5875 | True | low_price_per_m2, near_boulevard, near_supermarket | Uu tien don gia tren m2 thap |
| V1_003 | solution_2 | 2 | GV_035 | 0.5727 | True | near_boulevard, near_supermarket | Uu tien don gia tren m2 thap |
| V1_003 | solution_2 | 3 | GV_037 | 0.5669 | True | low_price_per_m2, near_boulevard, spacious | Uu tien don gia tren m2 thap |
| V1_003 | solution_2 | 4 | TB_008 | 0.5608 | True | low_price_per_m2, near_boulevard | Uu tien don gia tren m2 thap |
| V1_003 | solution_2 | 5 | GV_020 | 0.5399 | True | near_boulevard, near_supermarket | Uu tien don gia tren m2 thap |
| V1_003 | solution_1 | 1 | GV_010 | 0.59 | True | Đơn giá/m² thấp, Gần trục đường lớn, Rất gần siêu thị, Tiềm năng cho thuê tốt |  |
| V1_003 | solution_1 | 2 | GV_037 | 0.57 | True | Đơn giá/m² rất thấp, Diện tích rộng, Gần trục đường lớn |  |
| V1_003 | solution_1 | 3 | TB_008 | 0.56 | True | Đơn giá/m² rất thấp, Rất gần trục đường lớn, Gần siêu thị |  |
| V1_003 | solution_1 | 4 | GV_031 | 0.53 | True | Đơn giá/m² thấp, Diện tích tốt, Gần trục đường lớn, Gần siêu thị |  |
| V1_003 | solution_1 | 5 | GV_043 | 0.53 | True | Diện tích rộng, Gần trục đường lớn, Gần siêu thị |  |
| V1_004 | solution_2 | 1 | GV_009 | 0.7944 | True | near_park, good_price |  |
| V1_004 | solution_2 | 2 | GV_010 | 0.7424 | True | near_park, good_price |  |
| V1_004 | solution_2 | 3 | GV_011 | 0.7216 | True | near_park, good_price |  |
| V1_004 | solution_2 | 4 | TB_021 | 0.7208 | True | near_park |  |
| V1_004 | solution_2 | 5 | GV_012 | 0.7151 | True | near_park, good_price |  |
| V1_004 | solution_1 | 1 | GV_009 | 0.79 | True | Gần bệnh viện, Gần công viên, Giá tốt, Diện tích khá |  |
| V1_004 | solution_1 | 2 | GV_010 | 0.74 | True | Gần bệnh viện, Gần công viên, Giá tốt, Diện tích rộng |  |
| V1_004 | solution_1 | 3 | GV_011 | 0.72 | True | Rất gần bệnh viện, Gần công viên, Giá tốt |  |
| V1_004 | solution_1 | 4 | TB_021 | 0.72 | True | Cực gần bệnh viện, Gần công viên, Diện tích rộng |  |
| V1_004 | solution_1 | 5 | GV_012 | 0.72 | True | Cực gần bệnh viện, Gần công viên, Giá tốt |  |
| V1_005 | solution_2 | 1 | GV_002 | 0.6251 | True | good_price, near_supermarket | Can nha vua tui tien |
| V1_005 | solution_2 | 2 | GV_010 | 0.5994 | True | near_supermarket, near_school | Can nha vua tui tien |
| V1_005 | solution_2 | 3 | GV_011 | 0.556 | True | near_supermarket, near_school | Can nha vua tui tien |
| V1_005 | solution_2 | 4 | GV_008 | 0.5461 | True | near_school | Can nha vua tui tien |
| V1_005 | solution_2 | 5 | GV_015 | 0.5461 | True | near_supermarket, near_school | Can nha vua tui tien |
| V1_005 | solution_1 | 1 | GV_002 | 0.63 | True | Giá tốt, Gần siêu thị, Gần trường học |  |
| V1_005 | solution_1 | 2 | GV_010 | 0.6 | True | Gần siêu thị, Diện tích rộng, Gần trường học |  |
| V1_005 | solution_1 | 3 | GV_011 | 0.56 | True | Rất gần siêu thị, Giá tốt, Gần trường học |  |
| V1_005 | solution_1 | 4 | GV_015 | 0.55 | True | Cực gần siêu thị, Gần trường học, Diện tích tốt |  |
| V1_005 | solution_1 | 5 | GV_008 | 0.55 | True | Gần trường học, Gần siêu thị, Có thêm phòng ngủ |  |
| V1_006 | solution_2 | 1 | GV_008 | 0.7207 | True | good_price, near_school, good_kindergarten |  |
| V1_006 | solution_2 | 2 | TB_006 | 0.6794 | True | near_school, near_park, good_kindergarten |  |
| V1_006 | solution_2 | 3 | GV_010 | 0.6517 | True | good_price, near_school, near_park, near_supermarket, good_kindergarten |  |
| V1_006 | solution_2 | 4 | TB_021 | 0.6495 | True | near_school, near_park, good_kindergarten |  |
| V1_006 | solution_2 | 5 | GV_026 | 0.6268 | True | near_school, near_park, near_supermarket, good_kindergarten |  |
| V1_006 | solution_1 | 1 | GV_008 | 0.82 | True | Giá tốt, Rất gần trường mầm non, Gần trường học, Gần siêu thị | parking_within_1km |
| V1_006 | solution_1 | 2 | TB_021 | 0.79 | True | Rất gần trường mầm non, Gần trường học, Gần công viên, Gần bệnh viện, Diện tích tốt | parking_within_1km |
| V1_006 | solution_1 | 3 | TB_012 | 0.76 | True | Gần trường mầm non, Gần trường học, Gần công viên, Gần trục đường lớn | parking_within_1km |
| V1_006 | solution_1 | 4 | GV_022 | 0.73 | True | Gần trường mầm non, Gần trường học, Nhiều phòng ngủ | parking_within_1km |
| V1_006 | solution_1 | 5 | TB_006 | 0.71 | True | Rất gần trường mầm non, Gần trường học, Gần công viên, Gần siêu thị | parking_within_1km |
| V1_007 | solution_2 | 1 | GV_002 | 0.6237 | True | good_price, near_supermarket, near_boulevard, good_pharmacy | Khu nhieu tien ich |
| V1_007 | solution_2 | 2 | GV_020 | 0.6088 | True | near_supermarket, near_boulevard, good_pharmacy, good_gym | Khu nhieu tien ich |
| V1_007 | solution_2 | 3 | GV_010 | 0.5988 | True | near_supermarket, near_boulevard, good_pharmacy | Khu nhieu tien ich |
| V1_007 | solution_2 | 4 | GV_009 | 0.5911 | True | near_supermarket, good_pharmacy, good_gym | Khu nhieu tien ich |
| V1_007 | solution_2 | 5 | GV_011 | 0.5727 | True | near_supermarket, near_boulevard, good_pharmacy | Khu nhieu tien ich |
| V1_007 | solution_1 | 1 | GV_002 | 0.55 | True | Giá tốt, Gần siêu thị, Gần trục đường lớn, Gần nhà thuốc | Phòng gym (gym) gần nhà: chỉ 2/32 bất động sản có gym trong bán kính 1km (GV_009, GV_020), dữ liệu thưa khiến tiêu chí này khó đáp ứng. |
| V1_007 | solution_1 | 2 | GV_003 | 0.48 | True | Gần nhà thuốc, Gần trục đường lớn, Gần trường học | Phòng gym (gym) gần nhà: chỉ 2/32 bất động sản có gym trong bán kính 1km (GV_009, GV_020), dữ liệu thưa khiến tiêu chí này khó đáp ứng. |
| V1_007 | solution_1 | 3 | TB_008 | 0.31 | True | Diện tích rộng, Gần trục đường lớn, Gần bệnh viện, Gần siêu thị | Phòng gym (gym) gần nhà: chỉ 2/32 bất động sản có gym trong bán kính 1km (GV_009, GV_020), dữ liệu thưa khiến tiêu chí này khó đáp ứng. |
| V1_007 | solution_1 | 4 | GV_001 | 0.31 | True | Giá rất thấp | Phòng gym (gym) gần nhà: chỉ 2/32 bất động sản có gym trong bán kính 1km (GV_009, GV_020), dữ liệu thưa khiến tiêu chí này khó đáp ứng. |
| V1_007 | solution_1 | 5 | TB_005 | 0.29 | True | Gần nhà thuốc, Diện tích tốt | Phòng gym (gym) gần nhà: chỉ 2/32 bất động sản có gym trong bán kính 1km (GV_009, GV_020), dữ liệu thưa khiến tiêu chí này khó đáp ứng. |
| V1_008 | solution_2 | 1 | TB_035 | 0.6743 | True | low_price_per_m2, good_market | Muon khu sam uat de cho thue nhung gia tren m2 van phai thap |
| V1_008 | solution_2 | 2 | GV_010 | 0.582 | True | low_price_per_m2, near_boulevard, near_supermarket | Muon khu sam uat de cho thue nhung gia tren m2 van phai thap |
| V1_008 | solution_2 | 3 | GV_035 | 0.5582 | True | near_boulevard, near_supermarket | Muon khu sam uat de cho thue nhung gia tren m2 van phai thap |
| V1_008 | solution_2 | 4 | TB_008 | 0.4119 | True | low_price_per_m2, near_boulevard | Muon khu sam uat de cho thue nhung gia tren m2 van phai thap |
| V1_008 | solution_2 | 5 | GV_037 | 0.4022 | True | low_price_per_m2, near_boulevard, spacious | Muon khu sam uat de cho thue nhung gia tren m2 van phai thap |
| V1_008 | solution_1 | 1 | GV_010 | 0.62 | True | Đơn giá/m² thấp, Gần trục đường lớn, Diện tích rộng, Gần siêu thị |  |
| V1_008 | solution_1 | 2 | TB_008 | 0.59 | True | Đơn giá/m² rất thấp, Rất gần trục đường lớn, Diện tích rộng, Gần siêu thị |  |
| V1_008 | solution_1 | 3 | GV_035 | 0.58 | True | Đơn giá/m² thấp, Gần trục đường lớn, Diện tích rộng, Rất gần siêu thị, Nhiều tiện ích trong 1km |  |
| V1_008 | solution_1 | 4 | GV_037 | 0.57 | True | Đơn giá/m² rất thấp, Gần trục đường lớn, Diện tích rất rộng |  |
| V1_008 | solution_1 | 5 | GV_020 | 0.56 | True | Đơn giá/m² thấp, Rất gần trục đường lớn, Gần siêu thị, Diện tích tốt |  |
| V1_009 | solution_2 | 1 | GV_009 | 0.7531 | True | near_park, good_price | Muon noi yen tinh; dan tri cao; hop phong thuy; hang xom than thien |
| V1_009 | solution_2 | 2 | GV_010 | 0.7162 | True | near_park, good_price | Muon noi yen tinh; dan tri cao; hop phong thuy; hang xom than thien |
| V1_009 | solution_2 | 3 | TB_021 | 0.6883 | True | near_park | Muon noi yen tinh; dan tri cao; hop phong thuy; hang xom than thien |
| V1_009 | solution_2 | 4 | GV_011 | 0.6882 | True | near_park, good_price | Muon noi yen tinh; dan tri cao; hop phong thuy; hang xom than thien |
| V1_009 | solution_2 | 5 | GV_012 | 0.6808 | True | near_park, good_price | Muon noi yen tinh; dan tri cao; hop phong thuy; hang xom than thien |
| V1_009 | solution_1 | 1 | GV_009 | 0.753 | True | Gần bệnh viện, Gần công viên, Giá tốt, Gần trường học, Gần siêu thị | yên tĩnh; dân trí cao; hợp phong thủy; hàng xóm thân thiện |
| V1_009 | solution_1 | 2 | GV_010 | 0.716 | True | Diện tích rộng, Gần bệnh viện, Gần công viên, Gần trường học, Gần siêu thị, Gần trục đường lớn | yên tĩnh; dân trí cao; hợp phong thủy; hàng xóm thân thiện |
| V1_009 | solution_1 | 3 | TB_021 | 0.688 | True | Rất gần bệnh viện, Gần công viên, Gần trường học, Gần siêu thị, Gần trục đường lớn | yên tĩnh; dân trí cao; hợp phong thủy; hàng xóm thân thiện |
| V1_009 | solution_1 | 4 | GV_011 | 0.688 | True | Rất gần bệnh viện, Gần công viên, Giá tốt, Gần trường học, Gần siêu thị, Gần trục đường lớn | yên tĩnh; dân trí cao; hợp phong thủy; hàng xóm thân thiện |
| V1_009 | solution_1 | 5 | GV_012 | 0.681 | True | Rất gần bệnh viện, Gần công viên, Gần trường học, Gần siêu thị, Gần trục đường lớn | yên tĩnh; dân trí cao; hợp phong thủy; hàng xóm thân thiện |
| V1_010 | solution_2 | 1 | GV_010 | 0.7005 | True | near_supermarket, near_boulevard, good_cafe | nhung cung muon yen tinh |
| V1_010 | solution_2 | 2 | GV_011 | 0.634 | True | near_supermarket, near_boulevard, good_cafe | nhung cung muon yen tinh |
| V1_010 | solution_2 | 3 | GV_009 | 0.6156 | True | near_supermarket, good_cafe | nhung cung muon yen tinh |
| V1_010 | solution_2 | 4 | GV_012 | 0.5973 | True | near_supermarket, good_cafe | nhung cung muon yen tinh |
| V1_010 | solution_2 | 5 | GV_002 | 0.5259 | True | good_price, near_supermarket, near_boulevard | nhung cung muon yen tinh |
| V1_010 | solution_1 | 1 | GV_002 | 0.76 | True | Giá tốt, Gần siêu thị, Gần trục đường lớn, Nhiều quán cà phê |  |
| V1_010 | solution_1 | 2 | GV_010 | 0.66 | True | Diện tích rộng, Gần siêu thị, Gần trục đường lớn, Gần nhiều quán cà phê |  |
| V1_010 | solution_1 | 3 | GV_011 | 0.62 | True | Gần siêu thị, Gần trục đường lớn, Gần nhiều quán cà phê |  |
| V1_010 | solution_1 | 4 | GV_020 | 0.61 | True | Gần siêu thị, Gần trục đường lớn, Gần nhiều quán cà phê, Diện tích khá |  |
| V1_010 | solution_1 | 5 | GV_012 | 0.57 | True | Nhiều quán cà phê, Gần trục đường lớn, Gần siêu thị |  |

## Review Notes

- Use `X-only` for baseline cases and `X+Y` for measurable free-text cases, following `docs/validation_rubric.md`.
- `manual_review` means top1 differs; inspect whether difference is caused by valid Y handling, unsupported handling, or explanation quality.
- `V1_011`-`V1_013` were added after these outputs; rerun both solutions before final comparison.
