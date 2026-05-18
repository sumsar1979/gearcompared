#!/usr/bin/env python3
"""
ONE-SHOT: Replace all non-browser-verified ASINs with search URLs.
Only 5 ASINs confirmed live via browser on May 18, 2026.
Everything else gets a search URL (always live, carries affiliate tag).
"""
import json
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Only these 5 ASINs were confirmed live via browser
CONFIRMED_LIVE = {
    "B0CT95J8XH",  # Vari ComfortEdge
    "B0B422BBHT",  # FlexiSpot E7 Pro
    "B08572G1FG",  # Uplift V2 Commercial
    "B07SZHWCH5",  # Uplift V2 Standard
    "B008H4SLV6",  # Vitamix 5200
}

# Search queries for products being converted
SEARCH_QUERIES = {
    "B0B41YH9B6": "FlexiSpot E7 Plus standing desk",
    "B0DHS5X6WD": "Fully Jarvis standing desk",
    "B0G2KZDXDQ": "Autonomous SmartDesk Core",
    "B0FKH3GMZL": "SHW electric height adjustable standing desk",
    "B0B422ZYY1": "FlexiSpot EC1 standing desk frame",
    "B0C1VNFQS9": "FEZIBO electric standing desk",
    "B07L34K4BH": "Vitamix Explorian blender E310",
    "B0BCN28P8G": "Ninja Professional Plus Blender DUO BN751",
    "B07GV2SGRD": "Ninja BN701 Professional Plus Blender",
    "B07FDJMC9Q": "Ninja Air Fryer AF101",
    "B0CBSB2L7K": "Ninja DZ201 Foodi DualZone XL Air Fryer",
    "B0BD4BYR11": "COSORI Pro Gen 2 Air Fryer 5.8QT",
    "B07VHFMZHJ": "Instant Pot Vortex Plus 6QT Air Fryer",
    "B07JVD78TT": "Breville Bambino Plus Espresso Machine BES500BSS",
    "B0798G41DB": "Ninja 12-Cup Programmable Coffee Brewer",
    "B08C76KF7Q": "Hamilton Beach FlexBrew Trio Coffee Maker",
    "B00CH9QWOU": "Bodum Chambord French Press 34oz",
    "B005Z2F9T0": "KitchenAid Artisan 5 Quart Stand Mixer",
    "B08XY4D1P4": "KitchenAid Classic Plus 4.5 Quart Stand Mixer",
    "B07RTX3D8S": "Cuisinart SM-50 5.5 Quart Stand Mixer",
    "B000P9CWNY": "KitchenAid Pro 600 6 Quart Stand Mixer",
    "B001415B12": "Breville Die-Cast 4-Slice Smart Toaster",
    "B006OQSNYY": "Cuisinart Touch to Toast Leverless Toaster",
    "B08CK7TBP3": "KitchenAid 4-Slice Toaster KMT4117",
    "B00005OTWM": "Cuisinart CPT-122 2-Slice Toaster",
}


def make_search_url(query: str) -> str:
    return f"https://www.amazon.com/s?k={quote(query)}&tag=gearcompared2-20"


def main():
    changes = 0
    for cat_file in ['standing-desks.json', 'kitchen-appliances.json']:
        path = ROOT / 'data' / 'products' / cat_file
        with open(path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        for p in products:
            asin = p['asin']
            if asin in CONFIRMED_LIVE:
                continue
            query = SEARCH_QUERIES.get(asin, p['title'])
            new_url = make_search_url(query)
            if p.get('affiliateUrl') != new_url:
                p['affiliateUrl'] = new_url
                changes += 1
                print(f"  {asin} -> {query[:60]}")
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"\nTotal: {changes} ASINs converted to search URLs")
    print(f"Kept {len(CONFIRMED_LIVE)} ASINs as direct /dp/ links")
    
    # Regenerate manifests
    import subprocess
    result = subprocess.run(
        ['python', str(ROOT / 'scripts' / 'generate-manifests.py')],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    print(result.stdout)
    return changes


if __name__ == '__main__':
    import sys
    sys.exit(main())
