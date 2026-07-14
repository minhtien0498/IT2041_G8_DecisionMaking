"""Mapbox client thật: geocode_address (Geocoding v5), fetch_nearby_custom (Tilequery),
get_distance_to_place (geocode 1 lần + haversine tới từng candidate).

Cache in-memory theo (lat, lon làm tròn, amenity, radius) / theo address query để tiết
kiệm quota khi chạy lại nhiều validation case lúc dev (Mapbox có rate limit).
Fallback graceful (trả None/rỗng, không crash) khi thiếu MAPBOX_TOKEN hoặc lỗi network.
"""

import os

import requests

from .core import haversine_m

GEOCODING_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
TILEQUERY_URL = "https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/{lon},{lat}.json"

# Trung tâm Gò Vấp/Tân Bình, TP.HCM — dùng làm proximity bias cho geocoding.
DEFAULT_PROXIMITY = (106.68, 10.83)

# Mapping best-effort amenity_name -> (maki values, type substring) trong lớp `poi_label`
# của Mapbox Streets v8 (xem docs/data/tilesets/reference/mapbox-streets-v8). Dữ liệu
# nguồn từ OpenStreetMap nên không đầy đủ 100% — dùng kết hợp maki (chính xác hơn) +
# type substring (fallback, tăng recall) để tăng khả năng khớp.
AMENITY_KEYWORDS = {
    "school": {"maki": {"school", "college"}, "type_substr": ["school", "university"]},
    "hospital": {"maki": {"hospital", "doctor", "dentist"}, "type_substr": ["hospital", "clinic"]},
    "supermarket": {"maki": {"grocery"}, "type_substr": ["supermarket", "convenience"]},
    "market": {"maki": {"grocery"}, "type_substr": ["market", "supermarket", "greengrocer"]},
    "park": {"maki": {"park", "garden"}, "type_substr": ["park", "garden"]},
    "cafe": {"maki": {"cafe"}, "type_substr": ["cafe"]},
    "pharmacy": {"maki": {"pharmacy"}, "type_substr": ["pharmacy"]},
    "gym": {"maki": {"fitness-centre"}, "type_substr": ["sports centre", "gym", "fitness"]},
    "kindergarten": {"maki": set(), "type_substr": ["kindergarten", "nursery", "childcare"]},
}

_geocode_cache = {}
_tilequery_cache = {}


def _get_token():
    return os.environ.get("MAPBOX_TOKEN")


def geocode_address(query, proximity=DEFAULT_PROXIMITY, country="vn"):
    """Geocode 1 địa chỉ/địa điểm -> {"lat", "lon", "place_name"} hoặc None.

    Cache theo chuỗi query (lowercase, strip) để không tốn quota khi gọi lại.
    """
    token = _get_token()
    if not token:
        return None

    cache_key = query.strip().lower()
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]

    params = {
        "access_token": token,
        "limit": 1,
        "proximity": f"{proximity[0]},{proximity[1]}",
        "country": country,
        "language": "vi",
    }
    url = GEOCODING_URL.format(query=requests.utils.quote(query))

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        _geocode_cache[cache_key] = None
        return None

    features = data.get("features") or []
    if not features:
        _geocode_cache[cache_key] = None
        return None

    lon, lat = features[0]["center"]
    result = {"lat": lat, "lon": lon, "place_name": features[0].get("place_name", "")}
    _geocode_cache[cache_key] = result
    return result


def _matches_amenity(feature_props, amenity):
    keywords = AMENITY_KEYWORDS.get(amenity)
    if not keywords:
        return False
    maki = (feature_props.get("maki") or "").lower()
    ptype = (feature_props.get("type") or "").lower()
    pclass = (feature_props.get("class") or "").lower()
    if maki in keywords["maki"]:
        return True
    return any(s in ptype or s in pclass for s in keywords["type_substr"])


def fetch_nearby_one(lat, lon, amenity, radius_m):
    """Query Tilequery quanh (lat, lon) trong bán kính radius_m, lọc theo amenity.

    Trả về {"count", "nearest_m", "nearest_name"}. Cache theo (lat, lon làm tròn 5 số
    thập phân, amenity, radius_m).
    """
    token = _get_token()
    if not token:
        return {"count": 0, "nearest_m": None, "nearest_name": None}

    cache_key = (round(lat, 5), round(lon, 5), amenity, radius_m)
    if cache_key in _tilequery_cache:
        return _tilequery_cache[cache_key]

    params = {
        "access_token": token,
        "radius": radius_m,
        "layers": "poi_label",
        "limit": 50,
    }
    url = TILEQUERY_URL.format(lon=lon, lat=lat)

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        result = {"count": 0, "nearest_m": None, "nearest_name": None}
        _tilequery_cache[cache_key] = result
        return result

    matches = []
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        if _matches_amenity(props, amenity):
            distance = props.get("tilequery", {}).get("distance")
            matches.append((distance, props.get("name")))

    if not matches:
        result = {"count": 0, "nearest_m": None, "nearest_name": None}
    else:
        matches.sort(key=lambda m: (m[0] if m[0] is not None else float("inf")))
        result = {
            "count": len(matches),
            "nearest_m": round(matches[0][0]) if matches[0][0] is not None else None,
            "nearest_name": matches[0][1],
        }
    _tilequery_cache[cache_key] = result
    return result


def get_distance_m(lat1, lon1, lat2, lon2):
    """Haversine giữa 2 điểm — dùng cho get_distance_to_place sau khi đã geocode."""
    return haversine_m(lat1, lon1, lat2, lon2)
