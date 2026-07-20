"""Geoapify client thật: `geocode_address` (Geocoding v1) + `fetch_nearby_one`
(Places v2).

Cùng interface với `mapbox_client.py` ({"lat","lon","place_name"} cho geocode,
{"count","nearest_m","nearest_name"} cho fetch_nearby) để `tools.py` dùng qua
`enrichment_provider` mà không cần biết đang chạy provider nào — chỉ đổi
`SOLUTION1_ENRICHMENT_PROVIDER=geoapify` là tool chuyển hẳn sang gọi Geoapify thật.

Cache in-memory + fallback graceful (trả None/rỗng, không crash) khi thiếu
GEOAPIFY_API_KEY hoặc lỗi network, theo đúng tinh thần `mapbox_client.py`.
"""

import os

import requests

from .core import haversine_m

PLACES_URL = "https://api.geoapify.com/v2/places"
GEOCODE_URL = "https://api.geoapify.com/v1/geocode/search"

# Trung tâm Gò Vấp/Tân Bình, TP.HCM — dùng làm proximity bias cho geocoding/places.
DEFAULT_PROXIMITY = (106.68, 10.83)

# Mapping best-effort amenity -> category Geoapify Places (xem
# apidocs.geoapify.com/docs/places/#categories). Giữ cùng 9 loại tiện ích với
# `mapbox_client.AMENITY_KEYWORDS` để LLM hỏi được bất kỳ loại nào bất kể provider.
CATEGORY_MAP = {
    "school": ["education.school"],
    "kindergarten": ["childcare.kindergarten"],
    "park": ["leisure.park"],
    "hospital": ["healthcare.hospital", "healthcare.clinic_or_praxis.general"],
    "supermarket": ["commercial.supermarket"],
    "market": ["commercial.marketplace"],
    "cafe": ["catering.cafe"],
    "pharmacy": ["healthcare.pharmacy"],
    "gym": ["sport.fitness"],
}

_geocode_cache: dict = {}
_places_cache: dict = {}


def _get_key():
    return os.environ.get("GEOAPIFY_API_KEY")


def geocode_address(query, proximity=DEFAULT_PROXIMITY, country="vn"):
    """Geocode 1 địa chỉ/địa điểm -> {"lat", "lon", "place_name"} hoặc None.

    Cache theo chuỗi query (lowercase, strip) để không tốn quota khi gọi lại.
    """
    api_key = _get_key()
    if not api_key:
        return None

    cache_key = query.strip().lower()
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]

    params = {
        "text": query,
        "apiKey": api_key,
        "limit": 1,
        "bias": f"proximity:{proximity[0]},{proximity[1]}",
        "filter": f"countrycode:{country}",
        "lang": "vi",
    }

    try:
        resp = requests.get(GEOCODE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        _geocode_cache[cache_key] = None
        return None

    features = data.get("features") or []
    if not features:
        _geocode_cache[cache_key] = None
        return None

    props = features[0].get("properties", {})
    lon, lat = features[0]["geometry"]["coordinates"]
    result = {"lat": lat, "lon": lon, "place_name": props.get("formatted", "")}
    _geocode_cache[cache_key] = result
    return result


def fetch_nearby_one(lat, lon, amenity, radius_m):
    """Query Geoapify Places quanh (lat, lon) trong bán kính radius_m, lọc theo amenity.

    Trả về {"count", "nearest_m", "nearest_name"}. Cache theo (lat, lon làm tròn 5 số
    thập phân, amenity, radius_m).
    """
    api_key = _get_key()
    categories = CATEGORY_MAP.get(amenity)
    if not api_key or not categories:
        return {"count": 0, "nearest_m": None, "nearest_name": None}

    cache_key = (round(lat, 5), round(lon, 5), amenity, radius_m)
    if cache_key in _places_cache:
        return _places_cache[cache_key]

    params = {
        "categories": ",".join(categories),
        "filter": f"circle:{lon},{lat},{radius_m}",
        "bias": f"proximity:{lon},{lat}",
        "limit": 50,
        "apiKey": api_key,
    }

    try:
        resp = requests.get(PLACES_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        result = {"count": 0, "nearest_m": None, "nearest_name": None}
        _places_cache[cache_key] = result
        return result

    items = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        distance = props.get("distance")
        if distance is None:
            flon, flat = feature["geometry"]["coordinates"]
            distance = haversine_m(lat, lon, flat, flon)
        name = props.get("name") or props.get("formatted")
        items.append((distance, name))

    if not items:
        result = {"count": 0, "nearest_m": None, "nearest_name": None}
    else:
        items.sort(key=lambda item: (item[0] if item[0] is not None else float("inf")))
        result = {
            "count": len(items),
            "nearest_m": round(items[0][0]) if items[0][0] is not None else None,
            "nearest_name": items[0][1],
        }
    _places_cache[cache_key] = result
    return result


def get_distance_m(lat1, lon1, lat2, lon2):
    """Haversine giữa 2 điểm — dùng cho get_distance_to_place sau khi đã geocode."""
    return haversine_m(lat1, lon1, lat2, lon2)
