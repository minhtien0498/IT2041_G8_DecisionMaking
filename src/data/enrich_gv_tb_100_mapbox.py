"""Enrich the 100-property dataset with Mapbox POI features.

Input:
- data/go_vap_tan_binh_100.json

Outputs:
- data/mapbox/go_vap_tan_binh_100_enriched_mapbox_api.json
- data/mapbox/go_vap_tan_binh_100_enriched_mapbox_api_checkpoint.json
- data/mapbox/go_vap_tan_binh_100_mapbox_errors.json

The script uses Mapbox Tilequery on the `mapbox.mapbox-streets-v8` tileset,
layer `poi_label`, then filters returned POIs by best-effort `maki`, `type`,
and `class` metadata. It is intentionally batch/checkpoint friendly so the
run can be resumed without losing previous API results.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional convenience dependency
    load_dotenv = None

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
MAPBOX_DIR = DATA_DIR / "mapbox"

INPUT_FILE = DATA_DIR / "go_vap_tan_binh_100.json"
OUTPUT_FILE = MAPBOX_DIR / "go_vap_tan_binh_100_enriched_mapbox_api.json"
CHECKPOINT_FILE = MAPBOX_DIR / "go_vap_tan_binh_100_enriched_mapbox_api_checkpoint.json"
ERROR_FILE = MAPBOX_DIR / "go_vap_tan_binh_100_mapbox_errors.json"

TILEQUERY_URL = "https://api.mapbox.com/v4/mapbox.mapbox-streets-v8/tilequery/{lon},{lat}.json"
DEFAULT_RADIUS_M = 1000
DEFAULT_LIMIT = 50

AMENITY_KEYWORDS: dict[str, dict[str, set[str] | list[str]]] = {
    "school": {"maki": {"school", "college"}, "type_substr": ["school", "university"]},
    "kindergarten": {"maki": set(), "type_substr": ["kindergarten", "nursery", "childcare"]},
    "park": {"maki": {"park", "garden"}, "type_substr": ["park", "garden"]},
    "hospital": {"maki": {"hospital", "doctor", "dentist"}, "type_substr": ["hospital", "clinic"]},
    "supermarket": {"maki": {"grocery"}, "type_substr": ["supermarket", "convenience", "grocery"]},
    "market": {"maki": {"grocery"}, "type_substr": ["market", "supermarket", "greengrocer"]},
    "cafe": {"maki": {"cafe"}, "type_substr": ["cafe", "coffee"]},
    "pharmacy": {"maki": {"pharmacy"}, "type_substr": ["pharmacy", "drugstore"]},
    "gym": {"maki": {"fitness-centre"}, "type_substr": ["sports centre", "gym", "fitness"]},
    "boulevard": {"maki": set(), "type_substr": ["road", "street", "boulevard"]},
}


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_token() -> str:
    if load_dotenv is not None:
        load_dotenv(ROOT_DIR / ".env")
    token = os.environ.get("MAPBOX_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "Missing MAPBOX_TOKEN. Add it to .env or export MAPBOX_TOKEN before running this script."
        )
    return token


def matches_amenity(feature_props: dict[str, Any], amenity: str) -> bool:
    keywords = AMENITY_KEYWORDS.get(amenity)
    if not keywords:
        return False

    maki = str(feature_props.get("maki") or "").lower()
    poi_type = str(feature_props.get("type") or "").lower()
    poi_class = str(feature_props.get("class") or "").lower()
    name = str(feature_props.get("name") or "").lower()

    if maki in keywords["maki"]:
        return True
    return any(s in poi_type or s in poi_class or s in name for s in keywords["type_substr"])


def query_tilequery(
    *,
    token: str,
    lat: float,
    lon: float,
    radius_m: int,
    limit: int,
    timeout_s: int,
) -> list[dict[str, Any]]:
    params = {
        "access_token": token,
        "radius": radius_m,
        "layers": "poi_label",
        "limit": limit,
    }
    url = TILEQUERY_URL.format(lon=lon, lat=lat)
    response = requests.get(url, params=params, timeout=timeout_s)
    response.raise_for_status()
    payload = response.json()
    return payload.get("features", [])


def summarize_amenity(features: list[dict[str, Any]], amenity: str) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    for feature in features:
        props = feature.get("properties", {})
        if not matches_amenity(props, amenity):
            continue

        distance = props.get("tilequery", {}).get("distance")
        matches.append(
            {
                "name": props.get("name"),
                "distance_m": round(distance) if distance is not None else None,
                "maki": props.get("maki"),
                "type": props.get("type"),
                "class": props.get("class"),
            }
        )

    matches.sort(key=lambda item: item["distance_m"] if item["distance_m"] is not None else float("inf"))
    nearest = matches[0] if matches else {}
    return {
        "count": len(matches),
        "nearest_distance_m": nearest.get("distance_m"),
        "nearest_name": nearest.get("name"),
    }


def enrich_property(
    prop: dict[str, Any],
    *,
    token: str,
    amenities: list[str],
    radius_m: int,
    limit: int,
    timeout_s: int,
) -> dict[str, Any]:
    enriched = dict(prop)
    features = query_tilequery(
        token=token,
        lat=float(prop["latitude"]),
        lon=float(prop["longitude"]),
        radius_m=radius_m,
        limit=limit,
        timeout_s=timeout_s,
    )

    for amenity in amenities:
        summary = summarize_amenity(features, amenity)
        enriched[f"distance_to_nearest_{amenity}_m"] = summary["nearest_distance_m"]
        enriched[f"nearest_{amenity}_name"] = summary["nearest_name"]
        enriched[f"near_{amenity}_count_{radius_m // 1000}km"] = summary["count"]

    enriched["mapbox_enriched_at"] = datetime.now().isoformat(timespec="seconds")
    enriched["mapbox_radius_m"] = radius_m
    return enriched


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enrich 100-property dataset with Mapbox POI features.")
    parser.add_argument("--input", default=str(INPUT_FILE), help="Input clean dataset JSON.")
    parser.add_argument("--output", default=str(OUTPUT_FILE), help="Final enriched output JSON.")
    parser.add_argument("--checkpoint", default=str(CHECKPOINT_FILE), help="Checkpoint JSON path.")
    parser.add_argument("--errors", default=str(ERROR_FILE), help="Error log JSON path.")
    parser.add_argument("--radius-m", type=int, default=DEFAULT_RADIUS_M, help="Tilequery radius in meters.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Max Tilequery POIs per property.")
    parser.add_argument("--timeout-s", type=int, default=15, help="HTTP timeout in seconds.")
    parser.add_argument("--sleep-s", type=float, default=0.15, help="Sleep between properties to be gentle.")
    parser.add_argument("--max-records", type=int, default=None, help="Optional cap for smoke test runs.")
    parser.add_argument(
        "--amenities",
        nargs="+",
        default=["school", "kindergarten", "park", "hospital", "supermarket", "market", "cafe", "pharmacy", "gym"],
        choices=sorted(AMENITY_KEYWORDS.keys()),
        help="Amenity groups to derive from Mapbox POIs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = get_token()

    input_path = Path(args.input)
    output_path = Path(args.output)
    checkpoint_path = Path(args.checkpoint)
    errors_path = Path(args.errors)

    properties = load_json(input_path, [])
    if args.max_records is not None:
        properties = properties[: args.max_records]

    checkpoint = load_json(checkpoint_path, [])
    errors = load_json(errors_path, [])
    enriched_by_id = {item["property_id"]: item for item in checkpoint}

    started_at = time.time()
    for index, prop in enumerate(properties, start=1):
        property_id = prop["property_id"]
        if property_id in enriched_by_id:
            print(f"[{index}/{len(properties)}] skip checkpoint {property_id}")
            continue

        try:
            enriched = enrich_property(
                prop,
                token=token,
                amenities=args.amenities,
                radius_m=args.radius_m,
                limit=args.limit,
                timeout_s=args.timeout_s,
            )
            enriched_by_id[property_id] = enriched
            save_json(checkpoint_path, list(enriched_by_id.values()))
            print(f"[{index}/{len(properties)}] ok {property_id}")
        except Exception as exc:  # noqa: BLE001 - log and keep batch resumable
            error = {
                "property_id": property_id,
                "title": prop.get("title"),
                "lat": prop.get("latitude"),
                "lon": prop.get("longitude"),
                "error": repr(exc),
                "logged_at": datetime.now().isoformat(timespec="seconds"),
            }
            errors.append(error)
            save_json(errors_path, errors)
            print(f"[{index}/{len(properties)}] error {property_id}: {exc}")

        if args.sleep_s > 0:
            time.sleep(args.sleep_s)

    ordered = [enriched_by_id[p["property_id"]] for p in properties if p["property_id"] in enriched_by_id]
    save_json(output_path, ordered)
    save_json(errors_path, errors)

    elapsed_s = round(time.time() - started_at, 2)
    print("=== Mapbox enrichment summary ===")
    print("Input:", input_path)
    print("Output:", output_path)
    print("Checkpoint:", checkpoint_path)
    print("Errors:", errors_path)
    print("Records:", len(ordered), "/", len(properties))
    print("Errors:", len(errors))
    print("Elapsed seconds:", elapsed_s)


if __name__ == "__main__":
    main()
