# Validation Work Note

Ghi chú này tổng hợp các phần đã thêm, đã làm và cần làm trong đợt cập nhật validation cho đề tài DSS with Data: Smart Real Estate Advisory System.

## 1. Cac phan da them vao repo

### 1.1. Synthetic validation scenarios

- Them file `data/validation_50_scenarios.json`.
- Noi dung gom 50 kich ban nhu cau nguoi dung, chia theo 5 archetype:
  - Gia dinh co con nho.
  - Nguoi tre / young professional.
  - Nha dau tu.
  - Nguoi cao tuoi.
  - Cap doi.
- Moi archetype co 10 bien the khac nhau ve ngan sach, so phong ngu, trong so tieu chi va nguong danh gia.
- Cac scenario co cac thanh phan:
  - `hard_constraints`: ngan sach toi da, so phong ngu toi thieu.
  - `soft_preferences`: trong so cho gia, dien tich, truong hoc, cong vien, benh vien, sieu thi, truc duong lon.
  - `ground_truth_top5`: Top 5 duoc sinh bang reference scorer.
  - `candidates_after_filter`: so BDS con lai sau buoc loc cung.

### 1.2. Script sinh validation set

- Them file `src/eval/generate_validation_set.py`.
- Script nay tu dong tao 50 synthetic scenarios tu cac persona template.
- Co `random.seed(42)` de ket qua co the lap lai.
- Script tinh ground truth Top 5 bang mot reference scorer rieng.

Luu y quan trong: ground truth cua file nay van duoc sinh tu logic scoring rule-based, nen chi nen xem la technical validation, khong phai human-labeled validation.

### 1.3. Script danh gia pipeline

- Cap nhat `src/eval/evaluate_pipeline.py`.
- Script danh gia pipeline tren 50 scenarios bang cac metric:
  - Constraint Satisfaction Rate.
  - Precision@3, Precision@5.
  - Recall@3, Recall@5.
  - NDCG@3, NDCG@5.
  - Mean Average Precision.
  - Phan tich theo archetype.
  - Phan tich edge cases.

### 1.4. Bao cao ket qua validation

- Cap nhat `outputs/validation_report.md`.
- Them file `outputs/validation_summary.json`.
- Ket qua hien tai:
  - Tong so scenarios: 50.
  - Tap BDS: 37 BDS Go Vap da enrich POI.
  - CSR: 100.0%.
  - Precision@5: 76.8%.
  - Recall@5: 92.0%.
  - NDCG@5: 0.9200.
  - MAP: 0.9200.
- Co ghi nhan edge cases:
  - 4 scenarios khong co BDS phu hop.
  - 12 scenarios co it hon 5 candidates.

### 1.5. Survey form

- Them thu muc `survey/`, trong do co `survey/index.html`.
- Day la giao dien khao sat nhu cau mua nha.
- Muc dich: thu thap user preference that de tao human-labeled validation set cho giai doan tiep theo.

### 1.6. Midterm presentation output

- Them file `outputs/midterm_presentation.pdf`.
- File nay phuc vu trinh bay giua ky / bao cao tien do.

### 1.7. Validation analysis notebook

- Them file `notebooks/validation_analysis.ipynb`.
- Notebook nay dung de trinh bay phan data validation mot cach truc quan.
- Noi dung chinh:
  - Load `data/validation_50_scenarios.json`.
  - Load `outputs/validation_summary.json`.
  - Hien thi global metrics.
  - Phan tich metric theo archetype.
  - Liet ke edge cases.
  - Ghi ro gioi han cua synthetic validation va next step human-labeled validation.

## 2. Cac phan da lam trong dot nay

### 2.1. Mo rong validation tu 3 scenario len 50 scenario

- Truoc do pipeline chi co vai persona demo.
- Dot nay da tao tap 50 scenarios co do phu tot hon ve nhom nguoi dung va dieu kien loc.
- Muc tieu: kiem tra tinh on dinh cua recommender khi tham so nguoi dung thay doi.

### 2.2. Bo sung metric danh gia recommender

- Khong chi dung accuracy.
- Da them cac metric phu hop voi bai toan Top-K recommendation:
  - Precision@K de do do dung cua danh sach goi y.
  - Recall@K de do kha nang tim du cac item phu hop.
  - NDCG@K de do chat luong thu tu xep hang.
  - MAP de danh gia toan dien Top-K ranking.
  - CSR de dam bao khong vi pham rang buoc cung.

### 2.3. Them phan tich theo nhom nguoi dung

- Bao cao validation hien tai co breakdown theo 5 archetype.
- Dieu nay giup nhin ro nhom nao he thong hoat dong tot, nhom nao can cai thien.
- Nhom `couple` hien co metric thap hon do nhieu scenario co ngan sach / dieu kien qua chat, dan den it hoac khong co candidates.

### 2.4. Them phan tich edge cases

- He thong da duoc test voi truong hop:
  - Khong co BDS nao phu hop.
  - Co it hon 5 BDS sau loc.
- Pipeline hien xu ly duoc cac truong hop nay va khong bi crash.

### 2.5. Lam ro gioi han cua synthetic validation

- Da xac dinh diem yeu quan trong:
  - 50 scenarios duoc sinh bang code.
  - Ground truth cung duoc tinh tu scoring logic.
  - Vi vay khong the xem day la bang chung day du ve tinh dung dan cua recommendation trong thuc te.
- Nen trinh bay tap nay la technical validation / stress test / regression test.

### 2.6. Bo sung notebook de trinh bay data validation

- Da them notebook rieng cho validation analysis.
- Notebook khong thay the code trong `src/eval/`, ma chi doc outputs da sinh de tao bang, chart va nhan xet.
- Phu hop de demo voi thay hoac dua vao bao cao DSS with Data.

## 3. Cac phan can lam tiep theo

### 3.1. Tao human-labeled validation set

Can tao them file moi, de xuat:

```text
data/user_preference_validation.json
```

Noi dung nen gom 20-30 nhu cau nguoi dung that hoac ban-that:

```json
{
  "scenario_id": "REAL_001",
  "persona": "family",
  "user_need": "Gia dinh co 2 con nho, ngan sach duoi 6 ty, can 3 phong ngu, uu tien gan truong va cong vien.",
  "budget_max_million": 6000,
  "min_bedrooms": 3,
  "importance": {
    "school": 5,
    "park": 4,
    "hospital": 3,
    "supermarket": 4,
    "transport": 2
  },
  "human_relevance": {
    "GV_008": 5,
    "GV_035": 4,
    "GV_029": 4,
    "GV_031": 3,
    "GV_007": 2
  }
}
```

### 3.2. Dung survey de thu thap preference that

- Dung `survey/index.html` de thu thap 30-50 phan hoi.
- Moi phan hoi can co:
  - Ngan sach toi da.
  - So phong ngu toi thieu.
  - Muc uu tien 1-5 cho truong hoc, cong vien, benh vien, sieu thi, giao thong.
  - Nhu cau tu nhien bang text.

### 3.3. Cham diem relevance cho Top 5

Can co nhan danh gia tu nguoi that hoac nhom:

- Cho moi user need, chay pipeline lay Top 5 hoac Top 10 BDS.
- Nguoi cham cho diem tung BDS tu 1-5:
  - 5: rat phu hop.
  - 4: phu hop.
  - 3: tam chap nhan.
  - 2: it phu hop.
  - 1: khong phu hop.
- Dung diem nay lam ground truth doc lap de tinh NDCG@5, MAP va average relevance.

### 3.4. Mo rong property dataset

Tap hien tai chi co 37 BDS Go Vap, qua nho cho final.

Can mo rong bang:

- `docs/data_public.csv`: khoang 51k listing TP.HCM.
- Chon 500-1000 listing sach co du:
  - Price.
  - Area.
  - Bedrooms.
  - Bathrooms.
  - Latitude / Longitude.
  - District / Location.

### 3.5. Thay POI hardcode bang POI data that

Hien tai POI trong `src/demo/run_pipeline.py` dang hardcode mot so diem o Go Vap.

Can cai thien:

- Dung OpenStreetMap / Geofabrik Vietnam de lay POI.
- Tinh tu dong:
  - Khoang cach den truong hoc gan nhat.
  - Khoang cach den cong vien gan nhat.
  - Khoang cach den benh vien gan nhat.
  - Khoang cach den sieu thi / cho gan nhat.
  - So POI trong ban kinh 1km.

### 3.6. Tach ro 2 loai validation trong bao cao

Nen viet trong final report:

```text
Synthetic scenarios duoc dung de kiem tra do on dinh va tinh nhat quan cua thuat toan.
Human-labeled validation duoc dung de danh gia chat luong ra quyet dinh cua DSS.
```

Ly do:

- DSS recommendation khong co nhan dung/sai tuyet doi nhu classification.
- Chat luong quyet dinh nen duoc danh gia bang relevance score, constraint satisfaction va ranking quality.

## 4. Goi y commit message

```text
Add validation scenarios and DSS evaluation report
```

Hoac:

```text
Add synthetic validation pipeline and survey form
```

## 5. Ghi chu khi push

Nen noi voi nhom:

- Bo 50 scenarios hien tai la synthetic validation, phu hop de test pipeline.
- Chua nen claim day la bang chung recommendation dung voi nguoi mua that.
- De bai DSS with Data chac hon, can them human-labeled validation tu survey.
- Buoc tiep theo quan trong nhat la thu thap user preference va cham relevance cho Top 5 recommendation.
