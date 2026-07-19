"""Resume Overpass API enrichment for the 100-property GV/TB dataset.

Input:
- data/go_vap_tan_binh_100.json

Output:
- data/overpass/go_vap_tan_binh_100_enriched_overpass_api.json
- data/overpass/go_vap_tan_binh_100_enriched_overpass_api_checkpoint.json
- data/overpass/go_vap_tan_binh_100_overpass_errors.json

The script is intentionally compatible with
notebooks/enrich_gv_tb_100_overpass_pipeline.ipynb and can resume from the
checkpoint file. By default it only enriches missing property_id records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OVERPASS_DIR = DATA_DIR / "overpass"
CACHE_DIR = OVERPASS_DIR / "cache"

INPUT_PATH = DATA_DIR / "go_vap_tan_binh_100.json"
OUTPUT_PATH = OVERPASS_DIR / "go_vap_tan_binh_100_enriched_overpass_api.json"
CHECKPOINT_PATH = OVERPASS_DIR / "go_vap_tan_binh_100_enriched_overpass_api_checkpoint.json"
ERROR_LOG_PATH = OVERPASS_DIR / "go_vap_tan_binh_100_overpass_errors.json"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_STATUS_URL = "https://overpass-api.de/api/status"
USER_AGENT = "IT2041_G8_DecisionMaking/1.0 (overpass script)"

CATEGORY_ORDER = [
    "school",
    "park",
    "hospital",
    "supermarket",
    "market",
    "cafe",
    "boulevard",
]


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_m = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_m * c


def build_cache_key(lat: float, lon: float, radius_m: int) -> str:
    raw = f"{lat:.6f}|{lon:.6f}|{radius_m}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def overpass_query(lat: float, lon: float, radius_m: int) -> str:
    return f"""
[out:json][timeout:25];
(
  nwr["amenity"="school"](around:{radius_m},{lat},{lon});
  nwr["amenity"="kindergarten"](around:{radius_m},{lat},{lon});
  nwr["leisure"="park"](around:{radius_m},{lat},{lon});
  nwr["amenity"="hospital"](around:{radius_m},{lat},{lon});
  nwr["amenity"="clinic"](around:{radius_m},{lat},{lon});
  nwr["shop"="supermarket"](around:{radius_m},{lat},{lon});
  nwr["amenity"="marketplace"](around:{radius_m},{lat},{lon});
  nwr["amenity"="cafe"](around:{radius_m},{lat},{lon});
  way["highway"~"trunk|primary|secondary|trunk_link|primary_link|secondary_link"](around:{radius_m},{lat},{lon});
);
out center tags;
""".strip()


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)


def fetch_overpass_status_text(timeout_s: int) -> str:
    req = urllib.request.Request(
        OVERPASS_STATUS_URL,
        headers={"User-Agent": USER_AGENT},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_overpass_status(text: str) -> dict[str, Any]:
    info: dict[str, Any] = {
        "connected_as": None,
        "rate_limit": None,
        "slots_available_now": None,
        "raw_text": text,
    }

    match = re.search(r"Connected as:\s*(\S+)", text)
    if match:
        info["connected_as"] = match.group(1)

    match = re.search(r"Rate limit:\s*(\d+)", text)
    if match:
        info["rate_limit"] = int(match.group(1))

    match = re.search(r"(\d+)\s+slots available now\.", text)
    if match:
        info["slots_available_now"] = int(match.group(1))

    return info


def wait_for_overpass_slot(status_poll_s: int, timeout_s: int) -> dict[str, Any]:
    while True:
        status_text = fetch_overpass_status_text(timeout_s)
        status = parse_overpass_status(status_text)
        slots = status.get("slots_available_now")
        if slots is None or slots > 0:
            return status

        print(f"Chưa có slot khả dụng. Chờ {status_poll_s}s rồi kiểm tra lại /api/status...")
        time.sleep(status_poll_s)


def request_overpass(
    lat: float,
    lon: float,
    *,
    radius_m: int,
    force_refresh: bool,
    retry_count: int,
    timeout_s: int,
    base_sleep_s: float,
    status_poll_s: int,
) -> dict[str, Any]:
    cache_key = build_cache_key(lat, lon, radius_m)
    cache_path = CACHE_DIR / f"{cache_key}.json"

    if cache_path.exists() and not force_refresh:
        return read_json(cache_path, {})

    payload = urllib.parse.urlencode({"data": overpass_query(lat, lon, radius_m)}).encode("utf-8")
    req = urllib.request.Request(
        OVERPASS_URL,
        data=payload,
        headers={"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    last_error: Exception | None = None
    for attempt in range(1, retry_count + 1):
        try:
            wait_for_overpass_slot(status_poll_s, timeout_s)
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            write_json(cache_path, data)
            time.sleep(base_sleep_s)
            return data
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 429:
                wait_s = max(status_poll_s, 20)
            elif exc.code == 504:
                wait_s = attempt * 20
            else:
                wait_s = attempt * 5
            print(f"Lần thử {attempt} thất bại cho ({lat}, {lon}): {exc}. Chờ {wait_s}s...")
            time.sleep(wait_s)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            wait_s = attempt * 10
            print(f"Lần thử {attempt} thất bại cho ({lat}, {lon}): {exc}. Chờ {wait_s}s...")
            time.sleep(wait_s)

    raise RuntimeError(f"Overpass request failed after {retry_count} attempts: {last_error}")


def extract_point(element: dict[str, Any]) -> tuple[float | None, float | None]:
    if "lat" in element and "lon" in element:
        return element["lat"], element["lon"]
    center = element.get("center")
    if center and "lat" in center and "lon" in center:
        return center["lat"], center["lon"]
    return None, None


def classify_element(tags: dict[str, Any]) -> str | None:
    amenity = tags.get("amenity")
    leisure = tags.get("leisure")
    shop = tags.get("shop")
    highway = tags.get("highway")

    if amenity in {"school", "kindergarten"}:
        return "school"
    if leisure == "park":
        return "park"
    if amenity in {"hospital", "clinic"}:
        return "hospital"
    if shop == "supermarket":
        return "supermarket"
    if amenity == "marketplace":
        return "market"
    if amenity == "cafe":
        return "cafe"
    if highway in {"trunk", "primary", "secondary", "trunk_link", "primary_link", "secondary_link"}:
        return "boulevard"
    return None


def normalize_osm_results(raw: dict[str, Any], property_lat: float, property_lon: float) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {category: [] for category in CATEGORY_ORDER}

    for element in raw.get("elements", []):
        tags = element.get("tags", {})
        category = classify_element(tags)
        if not category:
            continue

        lat, lon = extract_point(element)
        if lat is None or lon is None:
            continue

        grouped[category].append(
            {
                "name": tags.get("name", f"osm_{element.get('id', 'unknown')}"),
                "lat": lat,
                "lon": lon,
                "distance_m": round(haversine_m(property_lat, property_lon, lat, lon)),
                "osm_type": element.get("type"),
                "osm_id": element.get("id"),
                "tags": tags,
            }
        )

    for category in grouped:
        grouped[category].sort(key=lambda item: item["distance_m"])

    return grouped


def build_feature_block(grouped: dict[str, list[dict[str, Any]]], count_radius_m: int) -> dict[str, Any]:
    features: dict[str, Any] = {}

    for category in CATEGORY_ORDER:
        items = grouped.get(category, [])
        if items:
            features[f"distance_to_nearest_{category}_m"] = items[0]["distance_m"]
            features[f"nearest_{category}_name"] = items[0]["name"]
            features[f"near_{category}_count_1km"] = sum(item["distance_m"] <= count_radius_m for item in items)
        else:
            features[f"distance_to_nearest_{category}_m"] = None
            features[f"nearest_{category}_name"] = None
            features[f"near_{category}_count_1km"] = 0

    return features


def enrich_property_with_overpass(prop: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    lat = prop["latitude"]
    lon = prop["longitude"]
    raw = request_overpass(
        lat,
        lon,
        radius_m=args.radius_m,
        force_refresh=args.force_refresh,
        retry_count=args.retry_count,
        timeout_s=args.timeout_s,
        base_sleep_s=args.sleep_s,
        status_poll_s=args.status_poll_s,
    )
    grouped = normalize_osm_results(raw, lat, lon)
    features = build_feature_block(grouped, count_radius_m=args.count_radius_m)

    enriched = dict(prop)
    enriched.update(features)
    enriched["enrichment_provider"] = "osm_overpass_api"
    enriched["enrichment_radius_m"] = args.radius_m
    enriched["enrichment_count_radius_m"] = args.count_radius_m
    enriched["api_result_count"] = len(raw.get("elements", []))
    return enriched


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--target-total", type=int, default=100)
    parser.add_argument("--max-records", type=int, default=None, help="Optional cap for this run only.")
    parser.add_argument("--radius-m", type=int, default=1500)
    parser.add_argument("--count-radius-m", type=int, default=1000)
    parser.add_argument("--sleep-s", type=float, default=2.0)
    parser.add_argument("--status-poll-s", type=int, default=15)
    parser.add_argument("--retry-count", type=int, default=5)
    parser.add_argument("--timeout-s", type=int, default=60)
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--save-every", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OVERPASS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    properties = read_json(INPUT_PATH, [])
    target_properties = properties[args.start_index : args.start_index + args.target_total]
    target_ids = {prop["property_id"] for prop in target_properties}

    enriched_properties = [] if args.force_refresh else read_json(CHECKPOINT_PATH, [])
    error_logs = [] if args.force_refresh else read_json(ERROR_LOG_PATH, [])
    existing_ids = {item["property_id"] for item in enriched_properties if item.get("property_id") in target_ids}

    remaining = [prop for prop in target_properties if args.force_refresh or prop["property_id"] not in existing_ids]
    if args.max_records is not None:
        remaining = remaining[: args.max_records]

    print(f"Mục tiêu trong dataset: {len(target_properties)}")
    print(f"Đã có checkpoint: {len(existing_ids)}")
    print(f"Sẽ xử lý lượt này: {len(remaining)}")
    print("Danh sách property_id:", [prop["property_id"] for prop in remaining])

    processed = 0
    for prop in remaining:
        try:
            enriched = enrich_property_with_overpass(prop, args)
            enriched_properties = [item for item in enriched_properties if item.get("property_id") != prop["property_id"]]
            enriched_properties.append(enriched)
            existing_ids.add(prop["property_id"])
            processed += 1
            print(f"Xong {prop['property_id']} | API elements: {enriched['api_result_count']}")

            if processed % args.save_every == 0:
                snapshot = sorted(enriched_properties, key=lambda x: x["property_id"])
                write_json(CHECKPOINT_PATH, snapshot)
                write_json(OUTPUT_PATH, snapshot)
                print(f"Đã lưu checkpoint/output: {len(existing_ids)} / {len(target_ids)}")
        except Exception as exc:  # noqa: BLE001 - keep batch resilient.
            error_logs.append(
                {
                    "property_id": prop["property_id"],
                    "district": prop.get("district"),
                    "latitude": prop.get("latitude"),
                    "longitude": prop.get("longitude"),
                    "error": str(exc),
                }
            )
            print(f"Lỗi tại {prop['property_id']}: {exc}")
            if args.stop_on_error:
                raise

    final_records = sorted(
        [item for item in enriched_properties if item.get("property_id") in target_ids],
        key=lambda x: x["property_id"],
    )
    write_json(CHECKPOINT_PATH, final_records)
    write_json(OUTPUT_PATH, final_records)
    write_json(ERROR_LOG_PATH, error_logs)

    print("Hoàn tất lượt chạy")
    print("Tổng số bản ghi output:", len(final_records))
    print("Tổng số lỗi:", len(error_logs))
    print("Output:", OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
