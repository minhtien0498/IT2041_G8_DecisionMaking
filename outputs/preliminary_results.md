# Kết quả sơ khởi và trạng thái output hiện tại

## 1. Trạng thái của file này

File này **không còn là báo cáo kết quả chính của workflow hiện tại**.

Nó được giữ lại như một ghi chú chuyển tiếp để phân biệt:
- kết quả `legacy` của giai đoạn midterm
- output đang tồn tại trong repo ở thời điểm hiện tại

## 2. Baseline legacy của midterm

Baseline cũ của nhóm được chạy trên:
- bộ `37` bất động sản Gò Vấp
- file `data/go_vap_30.json`
- file `data/go_vap_enriched.json`

Đây là pipeline cũ, dùng để:
- demo rule-based scoring ban đầu
- kiểm tra logic lọc và xếp hạng
- tạo các kết quả sơ khởi cho mốc giữa kỳ

Những kết quả đó **không đại diện cho workflow dữ liệu hiện tại** nữa.

## 3. Workflow dữ liệu hiện tại

Workflow hiện tại của nhóm đã chuyển sang bộ `100` căn:
- `data/go_vap_tan_binh_100.json`
- `data/go_vap_tan_binh_100_enriched.json`

Thành phần mới đã có:
- script tạo clean dataset: `src/data/prepare_gv_tb_100.py`
- notebook tạo clean dataset: `notebooks/prepare_gv_tb_100.ipynb`
- script enrich dataset: `src/data/enrich_gv_tb_100.py`
- notebook enrich dataset: `notebooks/enrich_gv_tb_100.ipynb`

## 4. Các output đang dùng trong repo

Các file output hiện có:
- `outputs/solution2_results.json`
- `outputs/validation_report.md`
- `outputs/validation_summary.json`

Lưu ý:
- `solution1_results.json` cũ đã được dọn vì thuộc về hướng rule-based đã bị loại
- các output còn lại hiện vẫn có thể còn phụ thuộc một phần vào pipeline hoặc dataset `legacy`
- nếu muốn chuyển hẳn sang bộ `100` căn, cần migrate toàn bộ pipeline/validation rồi chạy lại để sinh output mới

## 5. Kết luận

Nếu cần tài liệu tham chiếu lịch sử:
- dùng file này

Nếu cần output để tiếp tục phát triển:
- ưu tiên các file JSON/MD hiện có trong thư mục `outputs/`
- ưu tiên bộ dữ liệu `100` căn thay vì bộ `37` căn
