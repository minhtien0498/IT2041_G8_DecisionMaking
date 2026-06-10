"""
Pipeline 5.1: Rule-based Filtering → Scoring → Top 5 → Report

Chạy trên 30 BĐS Gò Vấp đã extract.
Tạo kết quả sơ khởi cho midterm.
"""

import json
import math
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
PROPERTIES_FILE = os.path.join(DATA_DIR, 'go_vap_30.json')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'outputs')


# ============================================================
# POI Reference Points in Gò Vấp (real locations)
# ============================================================
# Dùng tọa độ thật của các tiện ích nổi tiếng ở Gò Vấp
POI_DATABASE = {
    'school': [
        {'name': 'Trường THCS Nguyễn Du', 'lat': 10.8405, 'lon': 106.6550},
        {'name': 'Trường THPT Trần Hưng Đạo', 'lat': 10.8370, 'lon': 106.6635},
        {'name': 'Trường TH Lương Thế Vinh', 'lat': 10.8480, 'lon': 106.6520},
        {'name': 'Trường THCS Gò Vấp', 'lat': 10.8330, 'lon': 106.6450},
        {'name': 'Trường THPT Nguyễn Công Trứ', 'lat': 10.8450, 'lon': 106.6700},
        {'name': 'Trường TH Nguyễn Thái Bình', 'lat': 10.8520, 'lon': 106.6600},
        {'name': 'Trường Mầm non Sơn Ca', 'lat': 10.8380, 'lon': 106.6480},
        {'name': 'Trường TH Phạm Văn Chiêu', 'lat': 10.8495, 'lon': 106.6530},
    ],
    'park': [
        {'name': 'Công viên Gia Định', 'lat': 10.8190, 'lon': 106.6770},
        {'name': 'Công viên Phần mềm Quang Trung', 'lat': 10.8460, 'lon': 106.6330},
        {'name': 'Công viên phường 12', 'lat': 10.8350, 'lon': 106.6400},
        {'name': 'Công viên Làng Hoa', 'lat': 10.8430, 'lon': 106.6580},
    ],
    'hospital': [
        {'name': 'Bệnh viện Quận Gò Vấp', 'lat': 10.8380, 'lon': 106.6500},
        {'name': 'Bệnh viện 175', 'lat': 10.8570, 'lon': 106.6640},
        {'name': 'Phòng khám Đa khoa Sài Gòn', 'lat': 10.8450, 'lon': 106.6620},
    ],
    'supermarket': [
        {'name': 'Emart Gò Vấp', 'lat': 10.8345, 'lon': 106.6575},
        {'name': 'Co.opmart Quang Trung', 'lat': 10.8400, 'lon': 106.6470},
        {'name': 'VinMart Thống Nhất', 'lat': 10.8430, 'lon': 106.6650},
        {'name': 'Bách Hóa Xanh Quang Trung', 'lat': 10.8370, 'lon': 106.6420},
        {'name': 'Mega Market Quang Trung', 'lat': 10.8310, 'lon': 106.6390},
    ],
    'boulevard': [
        {'name': 'Quang Trung (trục chính)', 'lat': 10.8380, 'lon': 106.6450},
        {'name': 'Nguyễn Oanh', 'lat': 10.8420, 'lon': 106.6700},
        {'name': 'Phạm Văn Đồng', 'lat': 10.8200, 'lon': 106.6830},
        {'name': 'Lê Đức Thọ', 'lat': 10.8530, 'lon': 106.6580},
    ],
}


def haversine_m(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two lat/lon points."""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def enrich_property(prop):
    """Calculate distance to nearest POI for each category."""
    lat = prop['latitude']
    lon = prop['longitude']
    
    enriched = dict(prop)
    
    for poi_type, pois in POI_DATABASE.items():
        distances = [haversine_m(lat, lon, p['lat'], p['lon']) for p in pois]
        nearest_idx = distances.index(min(distances))
        
        enriched[f'distance_to_nearest_{poi_type}_m'] = round(min(distances))
        enriched[f'nearest_{poi_type}_name'] = pois[nearest_idx]['name']
        
        # Count POIs within 1km
        count_1km = sum(1 for d in distances if d <= 1000)
        enriched[f'near_{poi_type}_count_1km'] = count_1km
    
    return enriched


# ============================================================
# USER SCENARIO (Persona)
# ============================================================
USER_SCENARIOS = [
    {
        'scenario_id': 'family_01',
        'name': 'Gia đình có con nhỏ',
        'description': 'Gia đình 4 người, có 2 con nhỏ đang học cấp 1. Ngân sách dưới 8 tỷ, cần ít nhất 3 phòng ngủ. Ưu tiên gần trường học và công viên, gần siêu thị tiện mua sắm.',
        'hard_constraints': {
            'budget_max_million': 8000,
            'min_bedrooms': 3,
        },
        'soft_preferences': {
            'price': {
                'direction': 'lower_better',
                'weight': 0.25,
                'threshold_min': 3000,
                'threshold_max': 8000,
            },
            'distance_to_nearest_school_m': {
                'direction': 'lower_better',
                'weight': 0.25,
                'threshold_min': 0,
                'threshold_max': 2000,
            },
            'distance_to_nearest_park_m': {
                'direction': 'lower_better',
                'weight': 0.20,
                'threshold_min': 0,
                'threshold_max': 2000,
            },
            'distance_to_nearest_supermarket_m': {
                'direction': 'lower_better',
                'weight': 0.15,
                'threshold_min': 0,
                'threshold_max': 1500,
            },
            'area_m2': {
                'direction': 'higher_better',
                'weight': 0.15,
                'threshold_min': 30,
                'threshold_max': 150,
            },
        },
    },
    {
        'scenario_id': 'young_pro_01',
        'name': 'Người trẻ độc thân',
        'description': 'Nhân viên văn phòng 28 tuổi, ngân sách dưới 5.5 tỷ, cần ít nhất 2 phòng ngủ. Ưu tiên giá rẻ, gần siêu thị, gần trục đường lớn để tiện di chuyển.',
        'hard_constraints': {
            'budget_max_million': 5500,
            'min_bedrooms': 2,
        },
        'soft_preferences': {
            'price': {
                'direction': 'lower_better',
                'weight': 0.35,
                'threshold_min': 2000,
                'threshold_max': 5500,
            },
            'distance_to_nearest_supermarket_m': {
                'direction': 'lower_better',
                'weight': 0.25,
                'threshold_min': 0,
                'threshold_max': 1500,
            },
            'distance_to_nearest_boulevard_m': {
                'direction': 'lower_better',
                'weight': 0.20,
                'threshold_min': 0,
                'threshold_max': 2000,
            },
            'area_m2': {
                'direction': 'higher_better',
                'weight': 0.20,
                'threshold_min': 20,
                'threshold_max': 100,
            },
        },
    },
    {
        'scenario_id': 'investor_01',
        'name': 'Nhà đầu tư',
        'description': 'Nhà đầu tư BĐS, ngân sách dưới 15 tỷ. Ưu tiên giá/m² thấp (tiềm năng tăng giá), gần trục đường lớn, diện tích rộng, nhiều tiện ích xung quanh.',
        'hard_constraints': {
            'budget_max_million': 15000,
            'min_bedrooms': 1,
        },
        'soft_preferences': {
            'price_per_m2': {
                'direction': 'lower_better',
                'weight': 0.30,
                'threshold_min': 30,
                'threshold_max': 200,
            },
            'distance_to_nearest_boulevard_m': {
                'direction': 'lower_better',
                'weight': 0.25,
                'threshold_min': 0,
                'threshold_max': 2000,
            },
            'area_m2': {
                'direction': 'higher_better',
                'weight': 0.25,
                'threshold_min': 30,
                'threshold_max': 250,
            },
            'distance_to_nearest_supermarket_m': {
                'direction': 'lower_better',
                'weight': 0.20,
                'threshold_min': 0,
                'threshold_max': 1500,
            },
        },
    },
]


def normalize_score(value, threshold_min, threshold_max, direction):
    """Normalize value to [0, 1] based on direction."""
    if direction == 'lower_better':
        return max(0.0, min(1.0, (threshold_max - value) / (threshold_max - threshold_min)))
    elif direction == 'higher_better':
        return max(0.0, min(1.0, (value - threshold_min) / (threshold_max - threshold_min)))
    return 0.0


def get_attribute_value(prop, attr_name):
    """Get the raw value of an attribute for scoring."""
    if attr_name == 'price':
        return prop['price_million_vnd']
    elif attr_name == 'price_per_m2':
        return prop.get('price_per_m2_million', 0) or 0
    else:
        return prop.get(attr_name, 0) or 0


def run_pipeline(scenario, properties):
    """Run Pipeline 5.1 for a given user scenario."""
    print(f"\n{'='*70}")
    print(f"SCENARIO: {scenario['name']}")
    print(f"Mô tả: {scenario['description']}")
    print(f"{'='*70}")
    
    hc = scenario['hard_constraints']
    sp = scenario['soft_preferences']
    
    # ── Step 1: Hard constraint filtering ──
    print(f"\n📋 Bước 1: Rule-based Filtering")
    print(f"   Điều kiện: Giá ≤ {hc['budget_max_million']/1000:.1f} tỷ, Phòng ngủ ≥ {hc['min_bedrooms']}")
    
    candidates = []
    rejected = []
    for p in properties:
        reasons = []
        if p['price_million_vnd'] > hc['budget_max_million']:
            reasons.append(f"Giá {p['price_billion_vnd']} tỷ > {hc['budget_max_million']/1000:.1f} tỷ")
        if p['bedrooms'] < hc['min_bedrooms']:
            reasons.append(f"Phòng ngủ {p['bedrooms']} < {hc['min_bedrooms']}")
        
        if reasons:
            rejected.append((p, reasons))
        else:
            candidates.append(p)
    
    print(f"   Kết quả: {len(candidates)}/{len(properties)} BĐS qua lọc ({len(rejected)} bị loại)")
    
    if len(rejected) <= 10:
        for p, reasons in rejected:
            print(f"   ❌ {p['property_id']} ({p['title'][:40]}) — {'; '.join(reasons)}")
    else:
        for p, reasons in rejected[:5]:
            print(f"   ❌ {p['property_id']} ({p['title'][:40]}) — {'; '.join(reasons)}")
        print(f"   ... và {len(rejected)-5} BĐS khác")
    
    if not candidates:
        print("   ⚠️ Không có BĐS nào thỏa điều kiện!")
        return None
    
    # ── Step 2: Rule-based Scoring ──
    print(f"\n📊 Bước 2: Rule-based Scoring")
    print(f"   Tiêu chí & trọng số:")
    for attr_name, pref in sp.items():
        print(f"   • {attr_name}: weight={pref['weight']:.2f}, direction={pref['direction']}")
    
    scored = []
    for p in candidates:
        attributes = {}
        total_score = 0.0
        
        for attr_name, pref in sp.items():
            raw_value = get_attribute_value(p, attr_name)
            norm_score = normalize_score(
                raw_value,
                pref['threshold_min'],
                pref['threshold_max'],
                pref['direction']
            )
            contribution = norm_score * pref['weight']
            total_score += contribution
            
            attributes[attr_name] = {
                'value': round(raw_value, 1),
                'normalized_score': round(norm_score, 3),
                'weight': pref['weight'],
                'contribution_score': round(contribution, 4),
                'direction': pref['direction'],
            }
        
        scored.append({
            'property': p,
            'total_score': round(total_score, 4),
            'attributes': attributes,
        })
    
    # ── Step 3: Ranking ──
    scored.sort(key=lambda x: x['total_score'], reverse=True)
    
    # ── Step 4: Top 5 ──
    top5 = scored[:5]
    
    print(f"\n🏆 Bước 3 & 4: Ranking → Top 5")
    print(f"   {'Rank':<5} {'ID':<8} {'Score':<8} {'Giá(tỷ)':<10} {'DT(m²)':<9} {'PN':<4} {'WC':<4} {'Trường':<10} {'CV':<10} {'Siêu thị':<10} {'Title'}")
    print(f"   {'─'*5} {'─'*8} {'─'*8} {'─'*10} {'─'*9} {'─'*4} {'─'*4} {'─'*10} {'─'*10} {'─'*10} {'─'*30}")
    
    for rank, item in enumerate(top5, 1):
        p = item['property']
        print(f"   #{rank:<4} {p['property_id']:<8} {item['total_score']:.4f}  "
              f"{p['price_billion_vnd']:<10} {p['area_m2']:<9} {p['bedrooms']:<4} {p['bathrooms']:<4} "
              f"{p['distance_to_nearest_school_m']:>5}m    {p.get('distance_to_nearest_park_m','-'):>5}m    "
              f"{p.get('distance_to_nearest_supermarket_m','-'):>5}m    "
              f"{p['title'][:30]}")
    
    # ── Step 5: Score Breakdown for Top 1 ──
    print(f"\n📝 Bước 5: Chi tiết điểm số Top 1 ({top5[0]['property']['property_id']})")
    for attr_name, detail in top5[0]['attributes'].items():
        bar = '█' * int(detail['normalized_score'] * 20)
        print(f"   {attr_name:>38}: value={detail['value']:>8} → norm={detail['normalized_score']:.3f} × weight={detail['weight']:.2f} = {detail['contribution_score']:.4f}  {bar}")
    print(f"   {'TOTAL SCORE':>38}: {top5[0]['total_score']:.4f}")
    
    return {
        'scenario': scenario,
        'total_properties': len(properties),
        'after_filtering': len(candidates),
        'rejected_count': len(rejected),
        'top5': [
            {
                'rank': i + 1,
                'property_id': item['property']['property_id'],
                'title': item['property']['title'],
                'price_billion_vnd': item['property']['price_billion_vnd'],
                'area_m2': item['property']['area_m2'],
                'bedrooms': item['property']['bedrooms'],
                'bathrooms': item['property']['bathrooms'],
                'total_score': item['total_score'],
                'attributes': item['attributes'],
                'distance_to_nearest_school_m': item['property']['distance_to_nearest_school_m'],
                'distance_to_nearest_park_m': item['property'].get('distance_to_nearest_park_m'),
                'distance_to_nearest_hospital_m': item['property'].get('distance_to_nearest_hospital_m'),
                'distance_to_nearest_supermarket_m': item['property'].get('distance_to_nearest_supermarket_m'),
            }
            for i, item in enumerate(top5)
        ],
    }


def main():
    # Load data
    with open(PROPERTIES_FILE, 'r', encoding='utf-8') as f:
        properties = json.load(f)
    
    print(f"📂 Loaded {len(properties)} BĐS từ Gò Vấp")
    
    # Enrich with POI distances
    print(f"🔧 Enriching POI distances...")
    properties = [enrich_property(p) for p in properties]
    
    # Save enriched data
    enriched_file = os.path.join(DATA_DIR, 'go_vap_enriched.json')
    with open(enriched_file, 'w', encoding='utf-8') as f:
        json.dump(properties, f, ensure_ascii=False, indent=2)
    print(f"✅ Enriched data saved to {enriched_file}")
    
    # Run pipeline for each scenario
    all_results = []
    for scenario in USER_SCENARIOS:
        result = run_pipeline(scenario, properties)
        if result:
            all_results.append(result)
    
    # Save results
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    results_file = os.path.join(OUTPUT_DIR, 'pipeline_5_1_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ Tất cả kết quả đã lưu tại: {results_file}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
