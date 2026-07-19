"""Overpass client thật: `geocode_address` (OSM Nominatim) + `fetch_nearby_one`
(Overpass QL trên public instance).

Cùng interface với `mapbox_client.py`/`geoapify_client.py` để `tools.py` dùng qua
`enrichment_provider` mà không cần biết đang chạy provider nào — chỉ đổi
`SOLUTION1_ENRICHMENT_PROVIDER=overpass` là tool chuyển hẳn sang gọi Overpass thật.

Overpass/Nominatim là public OSM infrastructure: không cần API key nhưng cần
`User-Agent` hợp lệ (theo usage policy) và dễ bị rate-limit/timeout hơn 2 provider có
key kia (xem docs/provider_comparison_overpass_vs_geoapify.md) — cache in-memory để
giảm số lần gọi khi chạy lại nhiều case lúc dev. Fallback graceful (trả None/rỗng,
không crash) khi lỗi network/rate-limit.
"""

import requests

from .core import haversine_m

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "IT2041_G8_DecisionMaking/1.0 (solution1 live tool)"

# Trung tâm Gò Vấp/Tân Bình, TP.HCM — giữ tham số cho đồng nhất interface với 2
# client kia (Overpass/Nominatim không dùng proximity bias trực tiếp như Mapbox/Geoapify).
DEFAULT_PROXIMITY = (106.68, 10.83)

# Mapping best-effort amenity -> tag OSM (amenity=*/leisure=*/shop=*), cùng nhóm 9 loại
# tiện ích với `mapbox_client.AMENITY_KEYWORDS`/`geoapify_client.CATEGORY_MAP`.
TAG_QUERIES = {
    "school": ['nwr["amenity"="school"]'],
    "kindergarten": ['nwr["amenity"="kindergarten"]'],
    "park": ['nwr["leisure"="park"]'],
    "hospital": ['nwr["amenity"="hospital"]', 'nwr["amenity"="clinic"]'],
    "supermarket": ['nwr["shop"="supermarket"]'],
    "market": ['nwr["amenity"="marketplace"]'],
    "cafe": ['nwr["amenity"="cafe"]'],
    "pharmacy": ['nwr["amenity"="pharmacy"]'],
    "gym": ['nwr["leisure"="fitness_centre"]'],
}

_geocode_cache: dict = {}
_overpass_cache: dict = {}


def _element_latlon(element):
    if "lat" in element and "lon" in element:
        return element["lat"], element["lon"]
    center = element.get("center")
    if center and "lat" in center and "lon" in center:
        return center["lat"], center["lon"]
    return None, None


def geocode_address(query, proximity=DEFAULT_PROXIMITY, country="vn"):
    """Geocode 1 địa chỉ/địa điểm qua Nominatim -> {"lat", "lon", "place_name"} hoặc None.

    Cache theo chuỗi query (lowercase, strip) để không tốn quota khi gọi lại.
    """
    cache_key = query.strip().lower()
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]

    params = {
        "q": query,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": country,
        "accept-language": "vi",
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        _geocode_cache[cache_key] = None
        return None

    if not data:
        _geocode_cache[cache_key] = None
        return None

    item = data[0]
    result = {
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
        "place_name": item.get("display_name", ""),
    }
    _geocode_cache[cache_key] = result
    return result


def fetch_nearby_one(lat, lon, amenity, radius_m):
    """Query Overpass quanh (lat, lon) trong bán kính radius_m, lọc theo amenity.

    Trả về {"count", "nearest_m", "nearest_name"}. Cache theo (lat, lon làm tròn 5 số
    thập phân, amenity, radius_m).
    """
    tag_filters = TAG_QUERIES.get(amenity)
    if not tag_filters:
        return {"count": 0, "nearest_m": None, "nearest_name": None}

    cache_key = (round(lat, 5), round(lon, 5), amenity, radius_m)
    if cache_key in _overpass_cache:
        return _overpass_cache[cache_key]

    clauses = "\n".join(f'  {tf}(around:{radius_m},{lat},{lon});' for tf in tag_filters)
    query = f"[out:json][timeout:25];\n(\n{clauses}\n);\nout center tags;"
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"}

    try:
        resp = requests.post(OVERPASS_URL, data={"data": query}, headers=headers, timeout=25)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        result = {"count": 0, "nearest_m": None, "nearest_name": None}
        _overpass_cache[cache_key] = result
        return result

    items = []
    for element in data.get("elements", []):
        elat, elon = _element_latlon(element)
        if elat is None or elon is None:
            continue
        distance = haversine_m(lat, lon, elat, elon)
        name = element.get("tags", {}).get("name", f"osm_{element.get('id', 'unknown')}")
        items.append((distance, name))

    if not items:
        result = {"count": 0, "nearest_m": None, "nearest_name": None}
    else:
        items.sort(key=lambda item: item[0])
        result = {
            "count": len(items),
            "nearest_m": round(items[0][0]),
            "nearest_name": items[0][1],
        }
    _overpass_cache[cache_key] = result
    return result


def get_distance_m(lat1, lon1, lat2, lon2):
    """Haversine giữa 2 điểm — dùng cho get_distance_to_place sau khi đã geocode."""
    return haversine_m(lat1, lon1, lat2, lon2)
