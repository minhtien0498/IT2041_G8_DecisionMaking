# Geoapify API cURL Mẫu

File này chứa các lệnh `curl` mẫu để test `Geoapify Places API` bằng terminal hoặc đối chiếu khi cấu hình Postman.

Endpoint chính:

```text
https://api.geoapify.com/v2/places
```

Biến cần thay:

```text
YOUR_GEOAPIFY_API_KEY
```

## 1. cURL mẫu cho trường học quanh một tọa độ

```bash
curl "https://api.geoapify.com/v2/places?categories=education.school,childcare.kindergarten&filter=circle:106.675789,10.82735,1500&bias=proximity:106.675789,10.82735&limit=20&apiKey=YOUR_GEOAPIFY_API_KEY"
```

## 2. cURL mẫu cho siêu thị quanh một tọa độ

```bash
curl "https://api.geoapify.com/v2/places?categories=commercial.supermarket&filter=circle:106.675789,10.82735,1500&bias=proximity:106.675789,10.82735&limit=20&apiKey=YOUR_GEOAPIFY_API_KEY"
```

## 3. cURL mẫu cho quán cà phê quanh một tọa độ

```bash
curl "https://api.geoapify.com/v2/places?categories=catering.cafe&filter=circle:106.675789,10.82735,1500&bias=proximity:106.675789,10.82735&limit=20&apiKey=YOUR_GEOAPIFY_API_KEY"
```

## 4. Cấu hình tương đương trong Postman

- Method: `GET`
- URL: `https://api.geoapify.com/v2/places`
- Query params ví dụ:
  - `categories=education.school,childcare.kindergarten`
  - `filter=circle:106.675789,10.82735,1500`
  - `bias=proximity:106.675789,10.82735`
  - `limit=20`
  - `apiKey=YOUR_GEOAPIFY_API_KEY`

## 5. Lưu ý

- Geoapify cần API key hợp lệ.
- Theo tài liệu chính thức, Places API là HTTP `GET`.
- Free plan hiện có `3000 credits/day`; giới hạn gói Free là `up to 5 requests/second`.
- Mỗi `20` places trả về tương ứng `1 credit`.
