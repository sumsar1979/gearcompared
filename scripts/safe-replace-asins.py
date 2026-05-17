#!/usr/bin/env python3
"""Fix: Replace dead ASINs with Amazon search URLs (always work, carry affiliate tag).
Only keep ASINs verified live from pre-throttle audit + DuckDuckGo search index."""
import json
from pathlib import Path

ROOT = Path(r'C:\Users\Eland\.openclaw\workspace\gearcompared')

# CONFIRMED LIVE ASINs (pre-throttle browser audit + DuckDuckGo index)
CONFIRMED_LIVE = {
    "B0CT95J8XH",  # Vari ComfortEdge
    "B008H4SLV6",  # Vitamix 5200
    "B07FDJMC9Q",  # Ninja AF101
    "B0BD4BYR11",  # COSORI Pro Gen 2
    "B07VHFMZHJ",  # Instant Vortex Plus
    "B07JVD78TT",  # Breville Bambino Plus
    "B000P9CWNY",  # KitchenAid Pro 600
    "B001415B12",  # Breville Die-Cast Toaster
    "B006OQSNYY",  # Cuisinart Touch to Toast
}

# DuckDuckGo-verified replacements for standing desks
DGG_VERIFIED = {
    "B0CT94Z191": "B08572G1FG",  # Uplift V2 Commercial (2-leg) -> Uplift 2-leg V2-Commercial
    "B0DT3Y1X96": "B07SZHWCH5",  # Uplift V2 Standard -> Uplift 4-leg V2-Commercial
}

# Search query overrides for products without verified ASINs
SEARCH_QUERIES = {
    "B0B422BBHT": "FlexiSpot E7 Pro standing desk",
    "B0B41YH9B6": "FlexiSpot E7 Plus standing desk",
    "B0DHS5X6WD": "Fully Jarvis standing desk",
    "B0G2KZDXDQ": "Autonomous SmartDesk Core",
    "B0FKH3GMZL": "SHW electric standing desk",
    "B0B422ZYY1": "FlexiSpot EC1 standing desk",
    "B0C1VNFQS9": "FEZIBO electric standing desk",
    "B07L34K4BH": "Vitamix Explorian blender",
    "B0BCN28P8G": "Ninja Professional Plus Blender DUO",
    "B07GV2SGRD": "Ninja BN701 Professional Plus Blender",
    "B0CBSB2L7K": "Ninja DZ201 Foodi DualZone Air Fryer",
    "B0798G41DB": "Ninja 12-Cup Programmable Coffee Brewer",
    "B08C76KF7Q": "Hamilton Beach FlexBrew Trio Coffee Maker",
    "B00CH9QWOU": "Bodum Chambord French Press 34oz",
    "B005Z2F9T0": "KitchenAid Artisan 5 Quart Stand Mixer",
    "B08XY4D1P4": "KitchenAid Classic Plus 4.5 Quart Stand Mixer",
    "B07RTX3D8S": "Cuisinart SM-50 Stand Mixer",
    "B08CK7TBP3": "KitchenAid 4-Slice Toaster",
    "B00005OTWM": "Cuisinart CPT-122 Compact Toaster",
}

def make_search_url(query):
    from urllib.parse import quote
    return f"https://www.amazon.com/s?k={quote(query)}&tag=gearcompared2-20"

def update_product_file(filepath):
    data = json.load(open(filepath, encoding='utf-8'))
    changes = 0
    for product in data:
        asin = product.get('asin', '')
        
        # Skip confirmed live
        if asin in CONFIRMED_LIVE:
            continue
        
        # Use DuckDuckGo-verified replacement
        if asin in DGG_VERIFIED:
            product['asin'] = DGG_VERIFIED[asin]
            product['affiliateUrl'] = f"https://www.amazon.com/dp/{DGG_VERIFIED[asin]}?tag=gearcompared2-20"
            print(f"  DGG  {asin} -> {DGG_VERIFIED[asin]}")
            changes += 1
            continue
        
        # Use search URL fallback
        query = SEARCH_QUERIES.get(asin, product.get('title', asin))
        product['affiliateUrl'] = make_search_url(query)
        # Keep ASIN as-is but mark the affiliate URL as search-based
        print(f"  SRCH {asin}: {query[:50]}...")
        changes += 1
    
    if changes:
        json.dump(data, open(filepath, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f"  Saved {changes} changes to {filepath.name}")
    else:
        print(f"  No changes needed in {filepath.name}")
    return changes

def main():
    total = 0
    for fname in ['data/products/standing-desks.json', 'data/products/kitchen-appliances.json']:
        print(f"\n--- {fname} ---")
        total += update_product_file(ROOT / fname)
    print(f"\nTotal changes: {total}")

if __name__ == '__main__':
    main()
