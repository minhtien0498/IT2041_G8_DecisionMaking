# Validation Dataset Search - DSS with Data Real Estate Advisory

Ngay trong project hiện tại đã có validation, nhưng đó là **synthetic validation**:

- `data/validation_50_scenarios.json`: 50 kịch bản được sinh bằng code.
- `ground_truth_top5` được sinh từ reference scorer/rubric, chưa phải nhãn người dùng thật.
- Vì vậy bộ này phù hợp để test kỹ thuật, regression, edge cases và constraint satisfaction; chưa đủ để kết luận recommendation đúng với người mua thật.

## Kết luận tìm kiếm

Chưa tìm thấy public dataset phù hợp hoàn toàn với bài toán:

```text
user preference tại Việt Nam/TP.HCM
+ danh sách BĐS ứng viên
+ nhãn relevance/ranking do người thật chấm
```

Các dataset public thường chỉ có một trong hai phần:

1. **Property listing data**: giá, diện tích, vị trí, số phòng, mô tả.
2. **POI/context data**: trường học, bệnh viện, công viên, siêu thị, ranh giới hành chính.

Phần thiếu nhất là **human-labeled relevance**: với một nhu cầu cụ thể, căn nào phù hợp mức 1-5. Vì vậy hướng tốt nhất cho final là kết hợp:

```text
Listing dataset lớn hơn
+ POI data thật
+ survey/manual relevance labels
```

## Nguồn dữ liệu có thể dùng

| Nguồn | Vai trò | Dùng làm validation được không? | Ghi chú |
|---|---|---|---|
| `docs/data_public.csv` trong repo | Listing TP.HCM, khoảng 51k dòng | Có, để tạo holdout/test listing | Đây là nguồn tốt nhất hiện có vì cùng domain và có lat/lon ở một phần dữ liệu. |
| Ho Chi Minh City Real Estate Data 2025 - Kaggle | Listing BĐS TP.HCM | Có, nếu cần đối chiếu/tái tải nguồn gốc | Link: https://www.kaggle.com/datasets/cnglmph/ho-chi-minh-city-real-estate-data-2025 |
| `docs/vietnam_housing_dataset.csv` trong repo | Listing nhà ở Việt Nam, khoảng 30k dòng | Có, làm external/generalization test | Không tập trung TP.HCM; có thể thiếu tọa độ. |
| House Price Prediction Dataset Vietnam 2024 - Kaggle | Listing crawl từ BĐS Việt Nam | Có, làm external/generalization test | Link: https://www.kaggle.com/datasets/nguyentiennhan/vietnam-housing-dataset-2024 |
| OpenStreetMap / Geofabrik Vietnam | POI và đường sá | Có, để validate/enrich tiện ích | Link: https://download.geofabrik.de/asia/vietnam.html |
| GADM Vietnam boundaries | Ranh giới hành chính | Có, để chuẩn hóa quận/phường | Link: https://gadm.org/download_country.html |
| Real-estate recommender clickstream datasets trong paper | User interaction/relevance | Thường không public | Paper RE-RecSys dùng property + clickstream từ nền tảng thật, nhưng không thấy public dataset đi kèm: https://arxiv.org/abs/2404.16553 |

## Cách dùng từng loại validation

### 1. Data holdout validation

Dùng `docs/data_public.csv` để tạo tập listing lớn hơn:

```text
train/demo: 100-200 listing Gò Vấp hoặc TP.HCM
validation listing: 100-300 listing khác quận hoặc khác thời điểm
```

Mục tiêu:

- Test pipeline xử lý dữ liệu có ổn không.
- Test scoring có hoạt động trên listing mới không.
- Test không crash khi thiếu cột, thiếu lat/lon, giá/diện tích bất thường.

Hạn chế:

- Không đo được recommendation có đúng ý người mua thật không.

### 2. POI validation

Dùng OpenStreetMap/Geofabrik để thay cho POI hardcode trong `src/demo/run_pipeline.py`.

Mục tiêu:

- Kiểm tra khoảng cách tới trường, bệnh viện, công viên, siêu thị bằng dữ liệu thật.
- Tạo feature như `near_school_count_1km`, `distance_to_nearest_hospital_m`.

Hạn chế:

- Vẫn chưa có nhãn relevance của người dùng.

### 3. Human-labeled validation

Đây là phần cần bổ sung cho môn DSS with Data.

Quy trình đề xuất:

1. Thu thập 20-30 nhu cầu bằng `survey/index.html` hoặc Google Form.
2. Với mỗi nhu cầu, chạy pipeline lấy Top 5 hoặc Top 10.
3. Cho 2-3 người chấm từng BĐS theo relevance 1-5.
4. Lưu thành `data/user_preference_validation.json`.
5. Tính Average Relevance, NDCG@5, MAP@5, Constraint Satisfaction Rate.

Schema đề xuất:

```json
{
  "scenario_id": "REAL_001",
  "persona": "family",
  "user_need": "Gia đình 4 người, có 2 con nhỏ, ngân sách dưới 6 tỷ, cần 3 phòng ngủ, ưu tiên gần trường và công viên.",
  "hard_constraints": {
    "budget_max_million": 6000,
    "min_bedrooms": 3
  },
  "importance": {
    "school": 5,
    "park": 4,
    "hospital": 3,
    "supermarket": 4,
    "transport": 2
  },
  "candidate_ids": ["GV_008", "GV_035", "GV_029", "GV_031", "GV_007"],
  "human_relevance": {
    "GV_008": 5,
    "GV_035": 4,
    "GV_029": 4,
    "GV_031": 3,
    "GV_007": 2
  },
  "labelers": 2
}
```

## Khuyến nghị cho final

Nên trình bày 2 lớp validation:

1. **Technical validation**: 50 synthetic scenarios hiện có, dùng để chứng minh thuật toán ổn định, không vi phạm hard constraints và xử lý edge cases.
2. **Decision-quality validation**: 20-30 survey/manual-labeled scenarios, dùng để chứng minh Top 5 phù hợp với nhu cầu người dùng thật.

Nếu không đủ thời gian khảo sát nhiều, vẫn có thể làm bản tối thiểu:

```text
10 user scenarios
10 candidate properties/scenario
2 labelers
relevance scale 1-5
```

Như vậy nhóm có thể nói rõ: public dataset chỉ hỗ trợ listing/context, còn nhãn đúng-sai của quyết định phải được tạo bằng khảo sát hoặc manual labeling theo rubric.

## Tài liệu protocol chi tiết

Kế hoạch chi tiết để xây dựng tập validation nằm ở:

```text
docs/validation_dataset_plan.md
```

File này mô tả rõ:

- Cách tách `validation_properties.json`, `validation_user_scenarios.json`, `user_preference_validation.json`.
- Schema đề xuất cho từng file.
- Cách tạo candidate set công bằng giữa solution 2 và Solution 3.
- Rubric chấm relevance 1-5.
- Quy trình blind labeling.
- Metric so sánh solution: CSR@5, AvgRel@5, Precision@5, NDCG@5, MAP@5, Pairwise Win Rate, Top-5 Stability.
- Fallback nếu không kịp khảo sát thật.
