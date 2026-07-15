# Validation Rubric

File này là rubric chấm chung cho `Ấn` khi so sánh output của các solution.

Quy ước hiện tại:
- `Solution 1`: pipeline tuần tự hai LLM có guardrail của `Phú`
- `Solution 2`: hướng của `Quang`
- hướng rule-based `Solution 1` cũ đã bị loại

## 1. Mục tiêu

Rubric này dùng để trả lời 4 câu hỏi:
- Solution có vi phạm hard constraints không?
- Ranking có hợp nhu cầu persona không?
- Free-text có được xử lý đúng và minh bạch không?
- Explanation có bám output thật không?

## 2. Thứ tự ưu tiên khi chấm

1. `Constraint Satisfaction Rate (CSR)`
2. `Ranking quality`
3. `Unsupported requirement handling`
4. `Explanation quality`
5. `Latency`

Neu solution vi pham hard constraints nhieu, khong nen xep tot hon chi vi explanation hay.
## 2.1. Quy uoc ground truth `X + Y`

Khi case co free-text do duoc, `Ấn` cham ranking theo `X + Y`, khong chi theo `X`.

Trong do:
- `X` la cac tieu chi nen co san trong form/dataset: gia, dien tich, so phong ngu, truong, cong vien, benh vien, sieu thi, duong lon.
- `Y` la tieu chi sinh tu `user_need_text` va co the do bang POI/tool: cho, cafe, nha thuoc, gym, mam non.
- `Y_unsupported` la tieu chi chu quan hoac chua co data: yen tinh, dan tri cao, phong thuy, hang xom than thien, khu sam uat.

Quy tac nhan qua:
1. Neu case chi co `X`, ground truth dung ranking theo `base_score`/form criteria.
2. Neu case co `Y` do duoc, ground truth phai tinh ca `Y`, vi solution da co ly do hop le de doi thu hang.
3. Neu case co `Y_unsupported`, solution tot phai gan co trong `unsupported_requirements`, khong duoc cong diem ngam.
4. Neu solution dua `Y` vao diem, explanation phai noi ro `Y` lam rank nao thay doi. Neu khong noi, tru explanation quality.

Vi du cu the:
- `V1_006`: "gan truong mam non" la `Y` do duoc bang `distance_to_nearest_kindergarten_m`. Neu Top 1 doi tu can gan truong pho thong sang can gan mam non hon, day la hop le.
- `V1_007`: "gan nha thuoc va co phong gym" la `Y` do duoc bang pharmacy distance va gym count. Ranking nao bo qua hai tieu chi nay bi tru ranking quality.
- `V1_009`: "yen tinh, dan tri cao, phong thuy, hang xom than thien" la `Y_unsupported`. Solution nao van noi chac cac diem nay ma khong co du lieu bi tru nang explanation/unsupported.

## 3. Metric dinh luong chinh

| Metric | Muc dich | Cach doc |
|---|---|---|
| `CSR` | Kiem tra top5 co thoa rang buoc cung khong | Cang cao cang tot |
| `Precision@5` | Top5 co bao nhieu item relevant | Cang cao cang tot |
| `Recall@5` | Solution co lay du item relevant khong | Cang cao cang tot |
| `NDCG@5` | Item relevant co duoc day len cao khong | Cang cao cang tot |
| `MAP` | Chat luong ranking tong hop | Cang cao cang tot |
| `Latency_ms` | Toc do chay | Cang thap cang tot |

Neu output co `base_score` va `additional_score`, diem compare chinh dung `total_score = 0.7 * base_score + 0.3 * additional_score` theo contract demo hien tai. Neu mot solution khong co `additional_score`, xem nhu `additional_score = 0` cho case co `Y` do duoc, tru khi explanation/tool output chung minh no da xu ly `Y` bang cach khac.

## 4. Rule chot uu tien metric

- `CSR` la gate metric.
- Neu `CSR` thap hon doi thu ro ret, solution do bi xem la thua cho case do.
- Neu `CSR` bang nhau, so tiep `NDCG@5`, sau do `Precision@5`.
- `MAP` dung cho tong ket toan bo tap case, khong can qua nhan manh tung case.
- `Latency` chi dung lam tieu chi phu, khong ghi de ket qua recommendation.
- Voi case `X + Y`, so `NDCG@5` tren relevance sau khi da tinh ca `Y`; khong dung ground truth `X-only`.

## 5. Nhan xet dinh tinh bat buoc

Moi case nen co 4 nhan xet ngan:
- `constraint_note`: co vi pham hard constraint khong
- `ranking_note`: top1/top3 co hop persona khong
- `unsupported_note`: yeu cau nao bi gan co unsupported
- `explanation_note`: explanation co noi dung dung voi output khong

## 6. Cach cham unsupported requirement

| Tinh huong | Ket luan |
|---|---|
| Requirement khong do duoc va bi gan co ro rang | Dat |
| Requirement khong do duoc nhung solution van vo tinh tinh diem | Loi nang |
| Requirement do duoc nhung khong dua vao output/explanation | Loi vua |

## 7. Cach cham explanation

Explanation tot khi:
- nhac dung top1 hoac thay doi rank quan trong
- khong tu invent tieu chi khong co trong data
- co noi phan unsupported neu input co
- giai thich co bam `total_score`, `base_score`, `additional_score` neu co

Explanation yeu khi:
- noi chung chung
- noi sai thu tu rank
- noi gan truong/gan cong vien khi data khong ho tro
- bo qua unsupported requirements

## 8. Mau ket luan tung case

Dung format ngan sau:

```text
Case V1_001
- CSR: 1.0 vs 1.0
- Ranking: Solution 2 tot hon nhe do top1 hop family hon
- Unsupported: ca hai dat
- Explanation: Solution 2 ro hon
- Winner: Solution 2
```

## 9. Mau ket luan tong hop

Dung 3 dong tong hop:
- `solution_stability`: solution nao on dinh hon tren toan tap case
- `solution_flexibility`: solution nao xu ly free-text tot hon
- `final_recommendation`: solution nao hop bao ve final hon

## 10. Nguong danh gia de bao cao

| Muc | Dieu kien goi y |
|---|---|
| Tot | `CSR = 1.0` va `NDCG@5 >= 0.85` |
| On | `CSR >= 0.95` va `NDCG@5 >= 0.70` |
| Yeu | `CSR < 0.95` hoac explanation sai/khong minh bach |

## 11. Luu y cho `Ấn`

- Khong so sanh cong bang neu hai solution khac `output contract`.
- Khong dung chi synthetic validation de ket luan chat luong voi nguoi dung that.
- Neu dataset chay khac scope (`37` can vs `100` can), phai ghi ro trong bang compare.
- Voi Solution 1, can ghi ro case nao chi dung tien ich nen `X` va case nao co them tien ich dong `Y`.
- Voi Solution 1, can cham them grounding, tool-call correctness va explanation faithfulness.
- Khi viet report, can ghi ro: `X-only` dung cho case baseline; `X + Y` dung cho case free-text do duoc; `unsupported` dung cho case chu quan/khong co data.
