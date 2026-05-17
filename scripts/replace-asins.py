#!/usr/bin/env python3
"""Replace dead ASINs with verified-live ASINs across product JSON files."""
import json
from pathlib import Path

ROOT = Path(r'C:\Users\Eland\.openclaw\workspace\gearcompared')

# All verified replacements
REPLACEMENTS = {
    # Standing desks
    "B0B422BBHT": ("B08HKYL91J", "FlexiSpot E7 Pro"),
    "B0CT94Z191": ("B08DPLW5C1", "Uplift V2 Commercial"),
    "B0DT3Y1X96": ("B0CSZJYVYY", "Uplift V2 Standard"),
    "B0B41YH9B6": ("B09QH3VQMJ", "FlexiSpot E7 Plus"),
    "B0DHS5X6WD": ("B07THBWNKR", "Fully by Sway 60\"×30\" Standing Desk"),
    "B0G2KZDXDQ": ("B0G51HBPFN", "Autonomous SmartDesk Core"),
    "B0FKH3GMZL": ("B0BXG8BJG6", "SHW Electric Height Adjustable Standing Desk"),
    "B0B422ZYY1": ("B08C4PLK2T", "FlexiSpot EC1 Standing Desk"),
    "B0C1VNFQS9": ("B0BBQDRLWF", "FEZIBO Height Adjustable Electric Standing Desk"),
    # Kitchen blenders
    "B07L34K4BH": ("B0BWSLYK5H", "Vitamix Propel 510"),
    "B0BCN28P8G": ("B0BMGSZMW9", "Ninja BN751 Professional Plus DUO Blender"),
    "B07GV2SGRD": ("B0855B5Z6F", "Ninja Professional Plus Blender with Auto-iQ"),
    # Air fryers
    "B0CBSB2L7K": ("B089TQWJKK", "Ninja DZ201 Foodi DualZone XL Air Fryer"),
    # Coffee makers
    "B0798G41DB": ("B07S98411N", "Ninja 12-Cup Programmable Coffee Brewer"),
    "B08C76KF7Q": ("B095HZYNFM", "Hamilton Beach FlexBrew Trio Coffee Maker"),
    "B00CH9QWOU": ("B00008XEWG", "Bodum Chambord French Press, 34oz"),
    # Stand mixers
    "B005Z2F9T0": ("B0C59MGW5J", "KitchenAid Artisan Series 5-Quart Tilt-Head Stand Mixer"),
    "B08XY4D1P4": ("B0D44Y6B2D", "KitchenAid Classic Plus 4.5-Quart Tilt-Head Stand Mixer"),
    "B07RTX3D8S": ("B01H7R1EJY", "Cuisinart 5.5-Quart Stand Mixer SM-50"),
    # Toasters
    "B08CK7TBP3": ("B00Y2KG1DO", "KitchenAid KMT4116 4-Slice Long Slot Toaster"),
    "B00005OTWM": ("B009GQ034C", "Cuisinart CPT-122 2-Slice Compact Toaster"),
}

def update_product_file(filepath):
    data = json.load(open(filepath, encoding='utf-8'))
    changes = 0
    for product in data:
        old_asin = product.get('asin')
        if old_asin in REPLACEMENTS:
            new_asin, new_title = REPLACEMENTS[old_asin]
            product['asin'] = new_asin
            product['title'] = new_title
            product['affiliateUrl'] = f"https://www.amazon.com/dp/{new_asin}?tag=gearcompared2-20"
            print(f"  {old_asin} -> {new_asin} : {new_title[:60]}")
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
    print(f"\nTotal replacements: {total}")

if __name__ == '__main__':
    main()
