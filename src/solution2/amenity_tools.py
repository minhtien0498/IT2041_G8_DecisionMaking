"""Tool tìm tiện ích quanh một toạ độ — dùng OpenStreetMap Overpass API thật.

Thay cho bản mock trước đây (danh sách toạ độ tự nhập, chỉ phủ Gò Vấp và làm
listing Tân Bình bị chấm điểm 0 oan).

Dùng cùng endpoint/tag OSM với notebook enrich của member-3 để hai bên nhất quán.
Kết quả được cache xuống đĩa nên chạy lại không tốn network và tái lập được.
"""

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from .core import haversine_m

# Chỉ dùng server chính: các mirror công cộng khác (kumi.systems,
# private.coffee) thường timeout, xoay vòng sang chúng còn chậm hơn là retry.
# Server chính thỉnh thoảng 504/429 -> retry với backoff là đủ.
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "IT2041_G8_DecisionMaking/1.0 (solution2)"

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE_DIR = os.path.join(_ROOT, "data", "overpass", "cache")

# Bán kính tối thiểu khi truy vấn để còn tìm được "tiện ích gần nhất"
# kể cả khi trong bán kính người dùng yêu cầu không có cái nào.
_MIN_SEARCH_RADIUS_M = 2000

# Ánh xạ amenity_name -> selector OSM (theo đúng quy ước notebook của member-3)
AMENITY_OSM_SELECTORS = {
    "school": ['nwr["amenity"="school"]'],
    "kindergarten": ['nwr["amenity"="kindergarten"]'],
    "park": ['nwr["leisure"="park"]'],
    "hospital": ['nwr["amenity"="hospital"]', 'nwr["amenity"="clinic"]'],
    "supermarket": ['nwr["shop"="supermarket"]'],
    "market": ['nwr["amenity"="marketplace"]'],
    "cafe": ['nwr["amenity"="cafe"]'],
    "pharmacy": ['nwr["amenity"="pharmacy"]'],
    "gym": ['nwr["leisure"="fitness_centre"]'],
    "boulevard": [
        'way["highway"~"trunk|primary|secondary|trunk_link|primary_link|secondary_link"]'
    ],
}


def known_amenities():
    """amenity_name mà tool có thể đo được (dùng cho capability-aware reasoning)."""
    return set(AMENITY_OSM_SELECTORS)


def geocode(prop):
    """Lấy toạ độ của BĐS (dataset đã có sẵn lat/lon)."""
    return prop["latitude"], prop["longitude"]


def _build_query(lat, lon, amenity_name, radius_m):
    selectors = AMENITY_OSM_SELECTORS[amenity_name]
    body = "".join(f"  {s}(around:{radius_m},{lat},{lon});\n" for s in selectors)
    return f"[out:json][timeout:25];\n(\n{body});\nout center tags;"


def _cache_path(lat, lon, amenity_name, radius_m):
    key = f"{amenity_name}|{lat:.5f}|{lon:.5f}|{radius_m}"
    digest = hashlib.md5(key.encode()).hexdigest()[:16]
    return os.path.join(CACHE_DIR, f"{amenity_name}_{digest}.json")


def _fetch_elements(lat, lon, amenity_name, radius_m, *, max_retries=6):
    """Gọi Overpass (hoặc đọc cache) -> list phần tử OSM."""
    path = _cache_path(lat, lon, amenity_name, radius_m)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    query = _build_query(lat, lon, amenity_name, radius_m)
    data = urllib.parse.urlencode({"data": query}).encode()

    last_err = None
    for attempt in range(max_retries):
        req = urllib.request.Request(
            OVERPASS_URL, data=data, headers={"User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                payload = json.load(resp)
            elements = payload.get("elements", [])
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(elements, f, ensure_ascii=False)
            time.sleep(1.0)  # lịch sự với public API, tránh 429
            return elements
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                json.JSONDecodeError) as e:
            last_err = e
            time.sleep(min(2 ** attempt * 2, 20))  # backoff cho 429/504
    raise RuntimeError(f"Overpass thất bại cho {amenity_name} @({lat},{lon}): {last_err}")


def _element_latlon(el):
    if "lat" in el and "lon" in el:
        return el["lat"], el["lon"]
    center = el.get("center")
    if center:
        return center["lat"], center["lon"]
    return None


def summarize_elements(lat, lon, elements, radius_m):
    """Tính {count trong radius_m, khoảng cách tới cái gần nhất} từ phần tử OSM."""
    distances = []
    for el in elements:
        pos = _element_latlon(el)
        if pos:
            distances.append(haversine_m(lat, lon, pos[0], pos[1]))
    if not distances:
        return {"count": 0, "nearest_distance_m": None}
    return {
        "count": sum(1 for d in distances if d <= radius_m),
        "nearest_distance_m": round(min(distances)),
    }


def search_amenities(lat, lon, amenity_name, radius_m):
    """Đếm tiện ích trong bán kính + khoảng cách tới cái gần nhất (OSM thật).

    Truy vấn với bán kính >= _MIN_SEARCH_RADIUS_M để vẫn tìm được "cái gần nhất"
    khi trong bán kính yêu cầu không có tiện ích nào, nhưng `count` thì vẫn chỉ
    tính trong đúng `radius_m` người dùng hỏi.
    """
    if amenity_name not in AMENITY_OSM_SELECTORS:
        return {"count": 0, "nearest_distance_m": None}
    search_radius = max(radius_m, _MIN_SEARCH_RADIUS_M)
    elements = _fetch_elements(lat, lon, amenity_name, search_radius)
    return summarize_elements(lat, lon, elements, radius_m)
