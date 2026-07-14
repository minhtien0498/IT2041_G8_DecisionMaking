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

## 3. Metric dinh luong chinh

| Metric | Muc dich | Cach doc |
|---|---|---|
| `CSR` | Kiem tra top5 co thoa rang buoc cung khong | Cang cao cang tot |
| `Precision@5` | Top5 co bao nhieu item relevant | Cang cao cang tot |
| `Recall@5` | Solution co lay du item relevant khong | Cang cao cang tot |
| `NDCG@5` | Item relevant co duoc day len cao khong | Cang cao cang tot |
| `MAP` | Chat luong ranking tong hop | Cang cao cang tot |
| `Latency_ms` | Toc do chay | Cang thap cang tot |

## 4. Rule chot uu tien metric

- `CSR` la gate metric.
- Neu `CSR` thap hon doi thu ro ret, solution do bi xem la thua cho case do.
- Neu `CSR` bang nhau, so tiep `NDCG@5`, sau do `Precision@5`.
- `MAP` dung cho tong ket toan bo tap case, khong can qua nhan manh tung case.
- `Latency` chi dung lam tieu chi phu, khong ghi de ket qua recommendation.

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
