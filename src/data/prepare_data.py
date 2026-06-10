"""
Extract 30 clean Nhà riêng listings in Gò Vấp from data_public.csv.
Output: data/go_vap_30.json — ready for Pipeline 5.1.
"""

import csv
import json
import os
import math

INPUT_CSV = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'data_public.csv')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'go_vap_30.json')


def is_valid_row(r):
    """Check if a row meets all quality criteria."""
    if r.get('Property Type', '').strip() != 'Nhà riêng':
        return False
    if not r.get('Latitude', '').strip() or not r.get('Longitude', '').strip():
        return False
    if not r.get('Bedrooms', '').strip() or not r.get('Bathrooms', '').strip():
        return False
    try:
        beds = int(r['Bedrooms'])
        baths = int(r['Bathrooms'])
        if beds < 1 or beds > 10 or baths < 1 or baths > 10:
            return False
    except (ValueError, TypeError):
        return False
    try:
        price = float(r['Price'])
        if price < 500 or price > 30000:
            return False
    except (ValueError, TypeError):
        return False
    try:
        area = float(r['Area'])
        if area < 20 or area > 500:
            return False
    except (ValueError, TypeError):
        return False
    return True


def is_go_vap(r):
    """Check if listing is in Gò Vấp district."""
    text = (r.get('Location', '') + ' ' + r.get('Title', '')[:200]).lower()
    return 'gò vấp' in text or 'go vap' in text


def clean_row(r, idx):
    """Convert raw CSV row to clean JSON schema for pipeline 5.1."""
    price_million = float(r['Price'])
    area_m2 = float(r['Area'])
    
    # Extract ward from Location
    location = r.get('Location', '')
    ward = ''
    parts = location.split(',')
    for p in parts:
        p = p.strip()
        if 'Phường' in p or 'phường' in p:
            ward = p
            break
    
    return {
        'property_id': f'GV_{idx:03d}',
        'title': r.get('Title', '').strip()[:100],
        'district': 'Gò Vấp',
        'ward': ward,
        'location_raw': location,
        'price_million_vnd': price_million,
        'price_billion_vnd': round(price_million / 1000, 2),
        'area_m2': area_m2,
        'price_per_m2_million': round(price_million / area_m2, 2) if area_m2 > 0 else None,
        'bedrooms': int(r['Bedrooms']),
        'bathrooms': int(r['Bathrooms']),
        'floors': int(float(r['Floors'])) if r.get('Floors', '').strip() else None,
        'direction': r.get('Direction', '').strip() or None,
        'position': r.get('Position', '').strip() or None,
        'latitude': float(r['Latitude']),
        'longitude': float(r['Longitude']),
        'description_snippet': r.get('Description', '')[:300].strip() or None,
        # Amenity distances will be enriched later — placeholder
        'distance_to_nearest_school_m': None,
        'distance_to_nearest_park_m': None,
        'distance_to_nearest_hospital_m': None,
        'distance_to_nearest_supermarket_m': None,
        'distance_to_nearest_boulevard_m': None,
    }


def main():
    # Read CSV
    with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Filter
    go_vap = [r for r in rows if is_valid_row(r) and is_go_vap(r)]
    print(f'Found {len(go_vap)} clean listings in Gò Vấp')

    # Convert to clean JSON
    properties = [clean_row(r, i + 1) for i, r in enumerate(go_vap)]

    # Sort by price for readability
    properties.sort(key=lambda x: x['price_million_vnd'])

    # Summary stats
    prices = [p['price_million_vnd'] for p in properties]
    areas = [p['area_m2'] for p in properties]
    beds = [p['bedrooms'] for p in properties]
    
    print(f'\n=== Subset Summary ===')
    print(f'Count: {len(properties)}')
    print(f'Price range: {min(prices)/1000:.2f} - {max(prices)/1000:.2f} tỷ')
    print(f'Area range: {min(areas):.0f} - {max(areas):.0f} m²')
    print(f'Bedrooms: {min(beds)} - {max(beds)}')
    print(f'All have lat/lon: ✅')
    
    print(f'\nListing details:')
    for p in properties:
        print(f"  {p['property_id']} | {p['price_billion_vnd']} tỷ | {p['area_m2']}m² | "
              f"{p['bedrooms']}PN {p['bathrooms']}WC | "
              f"({p['latitude']:.6f}, {p['longitude']:.6f}) | {p['title'][:50]}")

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(properties, f, ensure_ascii=False, indent=2)
    
    print(f'\n✅ Saved to {OUTPUT_FILE}')


if __name__ == '__main__':
    main()
