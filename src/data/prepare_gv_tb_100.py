"""
Extract 100 clean "Nhà riêng" listings:
- 50 in Gò Vấp
- 50 in Tân Bình

Output: data/go_vap_tan_binh_100.json
"""

import csv
import json
import os
import unicodedata

INPUT_CSV = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "data_public.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "go_vap_tan_binh_100.json")

DISTRICTS = [
    ("Gò Vấp", "GV", ["go vap"]),
    ("Tân Bình", "TB", ["tan binh"]),
]


def normalize_text(text):
    """Lowercase and remove Vietnamese accents for keyword matching."""
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower()


def is_valid_row(row):
    """Check if a row meets quality criteria for the 100-house dataset."""
    if row.get("Property Type", "").strip() != "Nhà riêng":
        return False
    if not row.get("Latitude", "").strip() or not row.get("Longitude", "").strip():
        return False
    if not row.get("Bedrooms", "").strip() or not row.get("Bathrooms", "").strip():
        return False
    try:
        beds = int(float(row["Bedrooms"]))
        baths = int(float(row["Bathrooms"]))
        if beds < 1 or beds > 10 or baths < 1 or baths > 10:
            return False
    except (ValueError, TypeError):
        return False
    try:
        price = float(row["Price"])
        area = float(row["Area"])
        if price < 500 or price > 30000:
            return False
        if area < 20 or area > 500:
            return False
    except (ValueError, TypeError):
        return False
    return True


def detect_district(row):
    """Detect supported district from location/title."""
    text = normalize_text((row.get("Location", "") + " " + row.get("Title", "")[:200]).strip())
    for district_name, prefix, patterns in DISTRICTS:
        if any(pattern in text for pattern in patterns):
            return district_name, prefix
    return None, None


def extract_ward(location):
    """Extract ward-like part from location string if possible."""
    for part in (location or "").split(","):
        part = part.strip()
        if "Phường" in part or "phường" in part:
            return part
    return ""


def clean_row(row, district_name, prefix, idx):
    """Map raw CSV row into the shared JSON schema."""
    price_million = float(row["Price"])
    area_m2 = float(row["Area"])
    return {
        "property_id": f"{prefix}_{idx:03d}",
        "title": row.get("Title", "").strip()[:100],
        "district": district_name,
        "ward": extract_ward(row.get("Location", "")),
        "location_raw": row.get("Location", ""),
        "price_million_vnd": price_million,
        "price_billion_vnd": round(price_million / 1000, 2),
        "area_m2": area_m2,
        "price_per_m2_million": round(price_million / area_m2, 2) if area_m2 > 0 else None,
        "bedrooms": int(float(row["Bedrooms"])),
        "bathrooms": int(float(row["Bathrooms"])),
        "floors": int(float(row["Floors"])) if row.get("Floors", "").strip() else None,
        "direction": row.get("Direction", "").strip() or None,
        "position": row.get("Position", "").strip() or None,
        "latitude": float(row["Latitude"]),
        "longitude": float(row["Longitude"]),
        "description_snippet": row.get("Description", "")[:300].strip() or None,
        "distance_to_nearest_school_m": None,
        "distance_to_nearest_park_m": None,
        "distance_to_nearest_hospital_m": None,
        "distance_to_nearest_supermarket_m": None,
        "distance_to_nearest_boulevard_m": None,
    }


def main():
    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    grouped = {district_name: [] for district_name, _, _ in DISTRICTS}
    prefixes = {district_name: prefix for district_name, prefix, _ in DISTRICTS}

    for row in rows:
        if not is_valid_row(row):
            continue
        district_name, _ = detect_district(row)
        if district_name:
            grouped[district_name].append(row)

    for district_name in grouped:
        grouped[district_name].sort(key=lambda r: float(r["Price"]))

    quotas = {"Gò Vấp": 50, "Tân Bình": 50}
    selected = []

    for district_name, quota in quotas.items():
        district_rows = grouped[district_name][:quota]
        if len(district_rows) < quota:
            raise SystemExit(
                f"Not enough clean listings for {district_name}: found {len(district_rows)}, need {quota}"
            )
        prefix = prefixes[district_name]
        selected.extend(
            clean_row(row, district_name, prefix, idx + 1)
            for idx, row in enumerate(district_rows)
        )

    selected.sort(key=lambda item: (item["district"], item["price_million_vnd"]))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)

    counts = {}
    for district_name in quotas:
        counts[district_name] = sum(1 for item in selected if item["district"] == district_name)

    print("=== Dataset Summary ===")
    print("Output:", OUTPUT_FILE)
    print("Total:", len(selected))
    for district_name, count in counts.items():
        print(f"- {district_name}: {count}")


if __name__ == "__main__":
    main()
