# TODO Remove / Deprecate Outdated Files

File này ghi lại các file hiện đã cũ, dễ gây nhầm, hoặc chỉ nên giữ để tham chiếu lịch sử.

Ngày cập nhật: `2026-07-11`

## 1. File vẫn nên đánh dấu deprecated hoặc cân nhắc xóa / archive

### B. File enrich thủ công cũ ở thư mục data gốc

- `data/go_vap_tan_binh_100_enriched.json`

Lý do:
- Đây là output enrich theo cách thủ công / POI catalog cũ.
- Dễ bị nhầm với output API mới trong:
  - `data/overpass/`
  - `data/geoapify/`

Đề xuất:
- Giữ lại nếu cần so sánh baseline manual.
- Nếu không còn cần benchmark manual, nên chuyển vào thư mục archive hoặc đổi tên rõ hơn.

### C. Bộ dữ liệu legacy scope cũ

- `data/go_vap_30.json`
- `data/go_vap_enriched.json`

Lý do:
- Đây là bộ dữ liệu legacy Gò Vấp cũ.
- Không còn là scope chính của workflow `100` căn Gò Vấp + Tân Bình.

Đề xuất:
- Hiện tại **chưa nên xóa ngay** vì vẫn còn đang được một số pipeline / test / demo dùng thật.
- Cụ thể còn được tham chiếu trong:
  - `src/demo/run_solution2.py`
  - `src/eval/generate_validation_set.py`
  - `src/eval/evaluate_pipeline.py`
  - `tests/test_pipeline_contract.py`
  - `survey/index.html`
- Khi nào migrate xong toàn bộ các chỗ trên sang dataset mới thì mới nên chuyển sang archive hoặc xóa.

## 2. File root từng sinh ra trước đây và không nên tái tạo

Các file sau đã từng bị sinh ở `data/` gốc do notebook overpass cũ cấu hình sai:

- `data/go_vap_tan_binh_100_enriched_overpass_api.json`
- `data/go_vap_tan_binh_100_enriched_overpass_api_checkpoint.json`
- `data/go_vap_tan_binh_100_overpass_errors.json`

Trạng thái hiện tại:
- các file này đã được dọn khỏi repo
- các file này **không còn là output chuẩn**
- output chuẩn phải nằm trong:
  - `data/overpass/`

Đề xuất:
- Nếu các file root này xuất hiện lại trong tương lai, cần xóa và kiểm tra lại notebook đang chạy có đúng là `enrich_gv_tb_100_overpass_pipeline.ipynb` hay không.

## 3. File cache

Các thư mục cache sau không nên commit:

- `data/overpass/cache/`
- `data/geoapify/cache/`

Trạng thái:
- đã được thêm vào `.gitignore`

## 4. Kết luận

Hiện tại các file nên dùng làm chuẩn là:

- Overpass:
  - `notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb`
  - `data/overpass/`

- Geoapify:
  - `notebooks/enrich_gv_tb_100_geoapify_pipeline.ipynb`
  - `data/geoapify/`

Các file ngoài hai nhánh trên nếu phục vụ enrich thì cần được kiểm tra kỹ trước khi dùng để tránh nhầm workflow cũ và mới.

Ghi chú thêm:
- `notebooks/enrich_gv_tb_100.ipynb` và `notebooks/enrich_gv_tb_100_pipeline.ipynb` đã được dọn khỏi repo vì dễ gây nhầm với workflow API hiện tại.
