"""
Generate a comprehensive validation dataset for DSS evaluation.

Creates 50 diverse user scenarios covering:
- 5 persona archetypes × 10 parameter variations each
- Budget ranges from 3 tỷ to 20 tỷ
- Different bedroom requirements (1-5)
- Varying weight distributions across amenities
- Edge cases: very tight budget, conflicting preferences, etc.

Ground-truth Top 5 is computed independently using a reference scorer
(same math as pipeline but implemented separately to verify correctness).

Output: data/validation_50_scenarios.json
"""

import json
import math
import os
import random

random.seed(42)  # Reproducible

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ENRICHED_FILE = os.path.join(BASE_DIR, 'data', 'go_vap_enriched.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'validation_50_scenarios.json')

# ── Persona templates ──────────────────────────────────────────────
PERSONA_TEMPLATES = [
    {
        'archetype': 'family',
        'name_prefix': 'Gia đình',
        'budget_range': (5000, 10000),
        'bedrooms_range': (3, 5),
        'weight_profile': {
            'price': (0.15, 0.30),
            'distance_to_nearest_school_m': (0.20, 0.35),
            'distance_to_nearest_park_m': (0.10, 0.25),
            'distance_to_nearest_supermarket_m': (0.10, 0.20),
            'area_m2': (0.10, 0.20),
        },
    },
    {
        'archetype': 'young_professional',
        'name_prefix': 'Người trẻ',
        'budget_range': (3000, 6000),
        'bedrooms_range': (2, 3),
        'weight_profile': {
            'price': (0.25, 0.40),
            'distance_to_nearest_supermarket_m': (0.15, 0.30),
            'distance_to_nearest_boulevard_m': (0.15, 0.25),
            'area_m2': (0.10, 0.25),
        },
    },
    {
        'archetype': 'investor',
        'name_prefix': 'Nhà đầu tư',
        'budget_range': (8000, 20000),
        'bedrooms_range': (1, 3),
        'weight_profile': {
            'price_per_m2': (0.25, 0.40),
            'distance_to_nearest_boulevard_m': (0.15, 0.30),
            'area_m2': (0.15, 0.30),
            'distance_to_nearest_supermarket_m': (0.10, 0.25),
        },
    },
    {
        'archetype': 'elderly',
        'name_prefix': 'Người cao tuổi',
        'budget_range': (4000, 12000),
        'bedrooms_range': (2, 3),
        'weight_profile': {
            'distance_to_nearest_hospital_m': (0.30, 0.45),
            'distance_to_nearest_park_m': (0.20, 0.35),
            'price': (0.15, 0.25),
            'area_m2': (0.05, 0.15),
        },
    },
    {
        'archetype': 'couple',
        'name_prefix': 'Cặp đôi',
        'budget_range': (3500, 7000),
        'bedrooms_range': (2, 3),
        'weight_profile': {
            'price': (0.20, 0.35),
            'distance_to_nearest_supermarket_m': (0.20, 0.35),
            'distance_to_nearest_school_m': (0.10, 0.25),
            'area_m2': (0.10, 0.25),
        },
    },
]

# Threshold ranges per attribute (for normalization)
ATTR_THRESHOLDS = {
    'price':                              {'min_range': (2000, 4000), 'max_range': (6000, 20000), 'direction': 'lower_better'},
    'price_per_m2':                       {'min_range': (30, 50),     'max_range': (150, 250),    'direction': 'lower_better'},
    'distance_to_nearest_school_m':       {'min_range': (0, 0),      'max_range': (1500, 2500),  'direction': 'lower_better'},
    'distance_to_nearest_park_m':         {'min_range': (0, 0),      'max_range': (1500, 2500),  'direction': 'lower_better'},
    'distance_to_nearest_hospital_m':     {'min_range': (0, 0),      'max_range': (2000, 3000),  'direction': 'lower_better'},
    'distance_to_nearest_supermarket_m':  {'min_range': (0, 0),      'max_range': (1000, 2000),  'direction': 'lower_better'},
    'distance_to_nearest_boulevard_m':    {'min_range': (0, 0),      'max_range': (1500, 2500),  'direction': 'lower_better'},
    'area_m2':                            {'min_range': (20, 30),    'max_range': (100, 250),    'direction': 'higher_better'},
}

VARIANT_NAMES = {
    'family': [
        'trẻ có 1 con', 'trẻ có 2 con', 'đông con (4 người)', 'thu nhập trung bình',
        'thu nhập khá', 'ưu tiên trường quốc tế', 'ưu tiên công viên',
        'ưu tiên siêu thị', 'cần diện tích lớn', 'tiết kiệm ngân sách'
    ],
    'young_professional': [
        'mới ra trường', 'làm IT quận 1', 'freelancer', 'thu nhập 15-20tr',
        'thu nhập 25-35tr', 'cần gần đường lớn', 'thích khu yên tĩnh',
        'ưu tiên giá rẻ nhất', 'cần 3 phòng ngủ', 'muốn diện tích rộng'
    ],
    'investor': [
        'lướt sóng ngắn hạn', 'đầu tư dài hạn', 'cho thuê', 'ngân sách vừa',
        'ngân sách cao', 'ưu tiên mặt tiền', 'ưu tiên diện tích',
        'ưu tiên giá/m² thấp', 'gần siêu thị', 'khu dân cư sầm uất'
    ],
    'elderly': [
        'sống một mình', 'sống cùng vợ/chồng', 'cần gần bệnh viện',
        'ưu tiên công viên tập thể dục', 'ngân sách hưu trí', 'cần yên tĩnh',
        'gần chợ/siêu thị', 'muốn nhà rộng', 'ngân sách trung bình', 'gần con cháu'
    ],
    'couple': [
        'mới cưới', 'sắp có con', 'DINK (2 thu nhập)', 'ngân sách hạn chế',
        'ngân sách thoải mái', 'gần chợ/siêu thị', 'gần trường cho con',
        'cần diện tích lớn', 'muốn giá rẻ', 'khu an ninh tốt'
    ],
}


def generate_weights(profile):
    """Generate random weights from profile ranges, then normalize to sum=1."""
    raw = {}
    for attr, (lo, hi) in profile.items():
        raw[attr] = random.uniform(lo, hi)
    total = sum(raw.values())
    return {k: round(v / total, 3) for k, v in raw.items()}


def generate_thresholds(attrs):
    """Generate random min/max thresholds for each attribute."""
    result = {}
    for attr in attrs:
        info = ATTR_THRESHOLDS[attr]
        t_min = random.randint(*info['min_range'])
        t_max = random.randint(*info['max_range'])
        result[attr] = {
            'min': t_min,
            'max': t_max,
            'direction': info['direction'],
        }
    return result


# ── Reference scorer (independent implementation) ──────────────────
def ref_normalize(val, t_min, t_max, direction):
    if t_max == t_min:
        return 0.5
    if direction == 'lower_better':
        return max(0.0, min(1.0, (t_max - val) / (t_max - t_min)))
    else:
        return max(0.0, min(1.0, (val - t_min) / (t_max - t_min)))


def ref_get_value(prop, attr):
    if attr == 'price':
        return prop['price_million_vnd']
    elif attr == 'price_per_m2':
        return prop.get('price_per_m2_million', 0) or 0
    return prop.get(attr, 0) or 0


def compute_ground_truth(scenario, properties):
    """
    Independent reference scorer to compute ground-truth Top 5.
    Uses same math as pipeline but implemented separately.
    """
    hc = scenario['hard_constraints']
    sp = scenario['soft_preferences']

    # Filter
    candidates = [
        p for p in properties
        if p['price_million_vnd'] <= hc['budget_max_million']
        and p['bedrooms'] >= hc['min_bedrooms']
    ]

    # Score
    scored = []
    for c in candidates:
        total = 0.0
        for attr, config in sp.items():
            val = ref_get_value(c, attr)
            norm = ref_normalize(val, config['min'], config['max'], config['direction'])
            total += norm * config['weight']
        scored.append((c['property_id'], round(total, 4)))

    # Sort descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return [pid for pid, _ in scored[:5]]


def main():
    # Load enriched data
    with open(ENRICHED_FILE, 'r', encoding='utf-8') as f:
        properties = json.load(f)

    scenarios = []
    scenario_idx = 0

    for template in PERSONA_TEMPLATES:
        archetype = template['archetype']
        variants = VARIANT_NAMES[archetype]

        for i in range(10):
            scenario_idx += 1

            # Random budget & bedrooms
            budget = random.randint(*template['budget_range'])
            # Round to nearest 500
            budget = round(budget / 500) * 500
            bedrooms = random.randint(*template['bedrooms_range'])

            # Random weights (normalized to 1)
            weights = generate_weights(template['weight_profile'])

            # Random thresholds
            thresholds = generate_thresholds(weights.keys())

            # Build soft_preferences
            soft_prefs = {}
            for attr, w in weights.items():
                t = thresholds[attr]
                soft_prefs[attr] = {
                    'weight': w,
                    'direction': t['direction'],
                    'min': t['min'],
                    'max': t['max'],
                }

            scenario = {
                'scenario_id': f'VAL_{scenario_idx:03d}',
                'archetype': archetype,
                'name': f"{template['name_prefix']} – {variants[i]}",
                'hard_constraints': {
                    'budget_max_million': budget,
                    'min_bedrooms': bedrooms,
                },
                'soft_preferences': soft_prefs,
            }

            # Compute ground-truth Top 5
            gt = compute_ground_truth(scenario, properties)
            scenario['ground_truth_top5'] = gt

            # Count candidates (for reporting)
            hc = scenario['hard_constraints']
            n_candidates = sum(
                1 for p in properties
                if p['price_million_vnd'] <= hc['budget_max_million']
                and p['bedrooms'] >= hc['min_bedrooms']
            )
            scenario['candidates_after_filter'] = n_candidates

            scenarios.append(scenario)

    # Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)

    # Summary
    print(f"✅ Đã sinh {len(scenarios)} validation scenarios")
    print(f"   File: {OUTPUT_FILE}")
    print(f"\n   Phân bố theo archetype:")
    from collections import Counter
    arch_count = Counter(s['archetype'] for s in scenarios)
    for arch, cnt in arch_count.items():
        print(f"   - {arch}: {cnt} scenarios")

    # Check edge cases
    empty_gt = [s for s in scenarios if len(s['ground_truth_top5']) == 0]
    few_candidates = [s for s in scenarios if s['candidates_after_filter'] < 5]
    print(f"\n   Edge cases:")
    print(f"   - Scenarios với 0 candidates: {len(empty_gt)}")
    print(f"   - Scenarios với < 5 candidates: {len(few_candidates)}")
    if few_candidates:
        for s in few_candidates:
            print(f"     {s['scenario_id']}: {s['name']} — {s['candidates_after_filter']} candidates (budget={s['hard_constraints']['budget_max_million']}, beds≥{s['hard_constraints']['min_bedrooms']})")


if __name__ == '__main__':
    main()
