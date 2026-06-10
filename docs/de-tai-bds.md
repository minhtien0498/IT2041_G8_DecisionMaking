## Hệ thống tư vấn chọn bất động sản thông minh

**+ Mục tiêu:** Phát triển hệ thống khuyến nghị Top 5 căn hộ tối ưu dựa trên việc mô hình hóa sâu sắc các tiêu chí (tài chính, sở thích, nhu cầu) và các Luật suy luận về sự tương đồng/thay thế giữa các yếu tố bất động sản (BĐS).

---

**+ Thu thập tri thức:**

- 100–200 căn hộ mẫu (diện tích, giá, tiện ích, vị trí).
- Xác định Ma trận Tương đồng (Similarity Matrix) giữa các tiêu chí (Ví dụ: "Gần trường học" tương đồng với "Tiện ích giáo dục" ở mức 0.8).

---

**+ Xây dựng mô hình biểu diễn tri thức:** Đề xuất mô hình biểu diễn cho tri thức của hệ thống. Tri thức của hệ thống sẽ bao gồm ít nhất các nội dung sau:

- Mô hình biểu diễn thông tin BĐS gồm: *Giá – Diện tích – Tiện ích – Vị trí – Pháp lý*
- Mối quan hệ tương đồng giữa các tiêu chí.
- Các Luật suy luận cho việc xác định nhóm khách hàng, xác định bất động sản.

---

**+ Bài toán và các Thuật giải tương ứng:**

- Đề xuất các vấn đề cần giải quyết trong hệ thống và phương pháp giải tương ứng.
- Thuật toán Hệ thống Khuyến nghị (Recommender System) dựa trên luật và tiêu chí (Rule-based Filtering / Content-Based Filtering).
- LLM sinh mô tả và giải thích gợi ý.

---

Khi đó, cần phải làm rõ:

- Các tiêu chí này xác định dựa trên kiến thức hay thông tin nào? Nguồn?
- Biểu diễn các thông tin/tiêu chí như thế nào?
- So sánh 2 sản phẩm dựa trên yếu tố của BĐS.

---

## 🌸 Yêu cầu sản phẩm

- Form nhập tiêu chí người dùng → hiển thị top 3 gợi ý.
- Giải thích bằng văn bản tự nhiên.
- So sánh giữa kết quả hệ thống và các phương pháp khác.



## Mô tả cho AI

Tôi đang học môn Data-driven decision support system. Tôi đang lên ý tưởng cho bài cuối kì của mình. Đọc ảnh để xem đề tài mà tôi làm. Yêu cầu giữa kỳ của thầy tôi là mô tả đồ án cuối kì (slide) với các yêu cầu sau:

Yêu cầu cho slide:
1. Input: Người dùng nhập vào nhu cầu mà mình muốn. Mô tả thêm các thông tin hữu ích để hệ thống có thể phân tích. Sử dụng ngôn ngữ tự nhiên để mô tả.
2. Output: Top 5 bất động sản phù hợp với nhu cầu mà người dùng đã mô tả. Xếp hạng từ thấp đến cao và có giải thích.
3. EDA cơ bản về dữ liệu
4. Kế hoạch cho 2 solution
    - Solution 1: Sử dụng tập Dataset từ Kaggle năm 2025 (https://www.kaggle.com/datasets/cnglmph/ho-chi-minh-city-real-estate-data-2025). Ở đây sẽ chỉ bao gồm các thông tin cơ bản. Từ đây xây dựng pipeline để xử lí dữ liệu nếu cần thiết. Sau đó xây dựng "động cơ suy diễn" để phân tích dữ liệu dựa trên những gì mà tập dataset này cung cấp.

    - Solution 2: Sử dụng tập dataset của solution 1 nhưng ở bước xử lí dữ liệu thì sẽ có thêm các bước xử lí như sau: Dùng địa chỉ của mẫu dữ liệu để lấy được lat và long của nó => Sử dụng lat và long đó kết hợp với các Google Maps API để tìm các tiện ích xung quanh bất động sản đó => tạo nên tập dataset mới với các thông tin thêm => Từ đó xây dựng một "động cơ suy diễn" mới dựa trên tập dataset này.



