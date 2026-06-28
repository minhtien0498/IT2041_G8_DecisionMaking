"""
Enrich the 100-house clean dataset with POI distance features.

Input:
- data/go_vap_tan_binh_100.json

Output:
- data/go_vap_tan_binh_100_enriched.json
"""

import json
import math
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, "go_vap_tan_binh_100.json")
OUTPUT_FILE = os.path.join(DATA_DIR, "go_vap_tan_binh_100_enriched.json")

DISTRICT_POIS = {
    "Gò Vấp": {
        "school": [
            {"name": "Trường THCS Nguyễn Du", "lat": 10.8405, "lon": 106.6550},
            {"name": "Trường THPT Trần Hưng Đạo", "lat": 10.8370, "lon": 106.6635},
            {"name": "Trường TH Lương Thế Vinh", "lat": 10.8480, "lon": 106.6520},
            {"name": "Trường THCS Gò Vấp", "lat": 10.8330, "lon": 106.6450},
            {"name": "Trường THPT Nguyễn Công Trứ", "lat": 10.8450, "lon": 106.6700},
            {"name": "Trường TH Nguyễn Thái Bình", "lat": 10.8520, "lon": 106.6600},
            {"name": "Trường Mầm non Sơn Ca", "lat": 10.8380, "lon": 106.6480},
            {"name": "Trường TH Phạm Văn Chiêu", "lat": 10.8495, "lon": 106.6530},
        ],
        "park": [
            {"name": "Công viên Gia Định", "lat": 10.8190, "lon": 106.6770},
            {"name": "Công viên Phần mềm Quang Trung", "lat": 10.8460, "lon": 106.6330},
            {"name": "Công viên phường 12", "lat": 10.8350, "lon": 106.6400},
            {"name": "Công viên Làng Hoa", "lat": 10.8430, "lon": 106.6580},
        ],
        "hospital": [
            {"name": "Bệnh viện Quận Gò Vấp", "lat": 10.8380, "lon": 106.6500},
            {"name": "Bệnh viện 175", "lat": 10.8570, "lon": 106.6640},
            {"name": "Phòng khám Đa khoa Sài Gòn", "lat": 10.8450, "lon": 106.6620},
        ],
        "supermarket": [
            {"name": "Emart Gò Vấp", "lat": 10.8345, "lon": 106.6575},
            {"name": "Co.opmart Quang Trung", "lat": 10.8400, "lon": 106.6470},
            {"name": "VinMart Thống Nhất", "lat": 10.8430, "lon": 106.6650},
            {"name": "Bách Hóa Xanh Quang Trung", "lat": 10.8370, "lon": 106.6420},
            {"name": "Mega Market Quang Trung", "lat": 10.8310, "lon": 106.6390},
        ],
        "boulevard": [
            {"name": "Quang Trung", "lat": 10.8380, "lon": 106.6450},
            {"name": "Nguyễn Oanh", "lat": 10.8420, "lon": 106.6700},
            {"name": "Phạm Văn Đồng", "lat": 10.8200, "lon": 106.6830},
            {"name": "Lê Đức Thọ", "lat": 10.8530, "lon": 106.6580},
        ],
    },
    "Tân Bình": {
        "school": [
            {"name": "Trường THPT Nguyễn Thượng Hiền", "lat": 10.7998, "lon": 106.6524},
            {"name": "Trường THCS Hoàng Hoa Thám", "lat": 10.8038, "lon": 106.6402},
            {"name": "Trường TH Tân Sơn", "lat": 10.8123, "lon": 106.6420},
            {"name": "Trường THCS Ngô Sĩ Liên", "lat": 10.7928, "lon": 106.6507},
            {"name": "Trường THPT Tân Bình", "lat": 10.7903, "lon": 106.6466},
        ],
        "park": [
            {"name": "Công viên Hoàng Văn Thụ", "lat": 10.8019, "lon": 106.6648},
            {"name": "Công viên Gia Định", "lat": 10.8190, "lon": 106.6770},
            {"name": "Công viên Bàu Cát", "lat": 10.7936, "lon": 106.6396},
            {"name": "Công viên Tân Phước", "lat": 10.7898, "lon": 106.6535},
        ],
        "hospital": [
            {"name": "Bệnh viện Thống Nhất", "lat": 10.8011, "lon": 106.6478},
            {"name": "Bệnh viện Tân Bình", "lat": 10.7947, "lon": 106.6527},
            {"name": "Bệnh viện Phụ sản Mê Kông", "lat": 10.8011, "lon": 106.6566},
            {"name": "Bệnh viện Quốc tế CityCare Tân Bình", "lat": 10.8065, "lon": 106.6388},
        ],
        "supermarket": [
            {"name": "GO! Trường Chinh", "lat": 10.8068, "lon": 106.6248},
            {"name": "Lotte Mart Cộng Hòa", "lat": 10.8018, "lon": 106.6446},
            {"name": "Co.opmart Hoàng Văn Thụ", "lat": 10.7994, "lon": 106.6622},
            {"name": "VinMart Cộng Hòa", "lat": 10.8026, "lon": 106.6510},
        ],
        "boulevard": [
            {"name": "Cộng Hòa", "lat": 10.8010, "lon": 106.6485},
            {"name": "Trường Chinh", "lat": 10.8060, "lon": 106.6330},
            {"name": "Hoàng Văn Thụ", "lat": 10.7996, "lon": 106.6640},
            {"name": "Lý Thường Kiệt", "lat": 10.7889, "lon": 106.6520},
        ],
    },
}


def haversine_m(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two lat/lon points."""
    earth_radius_m = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius_m * c


def enrich_property(prop):
    """Calculate nearest POI distance and POI count within 1km."""
    district = prop["district"]
    if district not in DISTRICT_POIS:
        raise ValueError(f"Unsupported district for enrichment: {district}")

    lat = prop["latitude"]
    lon = prop["longitude"]
    pois_by_type = DISTRICT_POIS[district]

    enriched = dict(prop)

    for poi_type, pois in pois_by_type.items():
        distances = [haversine_m(lat, lon, poi["lat"], poi["lon"]) for poi in pois]
        nearest_idx = distances.index(min(distances))

        enriched[f"distance_to_nearest_{poi_type}_m"] = round(min(distances))
        enriched[f"nearest_{poi_type}_name"] = pois[nearest_idx]["name"]
        enriched[f"near_{poi_type}_count_1km"] = sum(1 for distance in distances if distance <= 1000)

    return enriched


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        properties = json.load(f)

    enriched_properties = [enrich_property(prop) for prop in properties]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched_properties, f, ensure_ascii=False, indent=2)

    district_counts = {}
    for prop in enriched_properties:
        district_counts[prop["district"]] = district_counts.get(prop["district"], 0) + 1

    print("=== Enriched dataset summary ===")
    print("Input:", INPUT_FILE)
    print("Output:", OUTPUT_FILE)
    print("Total properties:", len(enriched_properties))
    for district, count in sorted(district_counts.items()):
        print(f"- {district}: {count}")


if __name__ == "__main__":
    main()
