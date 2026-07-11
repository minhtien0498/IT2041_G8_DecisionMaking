# Overpass API cURL Mẫu

File này chứa các lệnh `curl` mẫu để test `Overpass API` bằng terminal hoặc đối chiếu khi cấu hình Postman.

Endpoint đang dùng trong notebook:

```text
https://overpass-api.de/api/interpreter
```

## 1. cURL mẫu đầy đủ

Ví dụ này gọi nhiều nhóm POI quanh một tọa độ ở Gò Vấp trong bán kính `1500m`.

```bash
curl -X POST "https://overpass-api.de/api/interpreter" \
  -H "User-Agent: IT2041_G8_DecisionMaking/1.0 test" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode 'data=
[out:json][timeout:25];
(
  nwr["amenity"="school"](around:1500,10.82735,106.675789);
  nwr["amenity"="kindergarten"](around:1500,10.82735,106.675789);
  nwr["leisure"="park"](around:1500,10.82735,106.675789);
  nwr["amenity"="hospital"](around:1500,10.82735,106.675789);
  nwr["amenity"="clinic"](around:1500,10.82735,106.675789);
  nwr["shop"="supermarket"](around:1500,10.82735,106.675789);
  nwr["amenity"="marketplace"](around:1500,10.82735,106.675789);
  nwr["amenity"="cafe"](around:1500,10.82735,106.675789);
  way["highway"~"trunk|primary|secondary|trunk_link|primary_link|secondary_link"](around:1500,10.82735,106.675789);
);
out center tags;
'
```

## 2. cURL mẫu rút gọn

Ví dụ này nhẹ hơn để test nhanh, giảm nguy cơ bị `429 Too Many Requests`.

```bash
curl -X POST "https://overpass-api.de/api/interpreter" \
  -H "User-Agent: IT2041_G8_DecisionMaking/1.0 test" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode 'data=
[out:json][timeout:25];
(
  nwr["amenity"="school"](around:800,10.82735,106.675789);
  nwr["amenity"="hospital"](around:800,10.82735,106.675789);
  nwr["shop"="supermarket"](around:800,10.82735,106.675789);
);
out center tags;
'
```

## 3. Test API status

Lệnh này dùng để xem trạng thái hiện tại của public Overpass server.

```bash
curl "https://overpass-api.de/api/status" \
  -H "User-Agent: IT2041_G8_DecisionMaking/1.0 status-check"
```

## 4. Cấu hình tương đương trong Postman

- Method: `POST`
- URL: `https://overpass-api.de/api/interpreter`
- Headers:
  - `User-Agent: IT2041_G8_DecisionMaking/1.0 test`
  - `Content-Type: application/x-www-form-urlencoded`
- Body:
  - chọn `x-www-form-urlencoded`
  - key: `data`
  - value: toàn bộ query Overpass

## 5. Lưu ý

- Public Overpass dễ bị `429` nếu gọi quá dày.
- Nên test bằng query nhỏ trước.
- Nếu cần đối chiếu đúng query notebook đang dùng, xem cell `overpass_query(...)` trong notebook `enrich_gv_tb_100_overpass_pipeline.ipynb`.
