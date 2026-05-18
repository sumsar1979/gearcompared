#!/usr/bin/env python3
"""
FINAL FIX: Convert ALL /dp/ links to Amazon search URLs.
No more per-ASIN whitelist. Every affiliate link uses amazon.com/s?k=...
with gearcompared2-20 tag. Search URLs are always live.
"""
import json
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Map remaining /dp/ ASINs to good search queries
QUERIES = {
    "B0CT95J8XH": "Vari ComfortEdge Electric Standing Desk",
    "B0B422BBHT": "FlexiSpot E7 Pro Electric Standing Desk",
    "B08572G1FG": "Uplift V2 Standing Desk Commercial",
    "B07SZHWCH5": "Uplift V2 Standing Desk Standard",
    "B008H4SLV6": "Vitamix 5200 Blender",
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
            old_url = p.get('affiliateUrl', '')
            if '/dp/' not in old_url:
                continue  # already a search URL
            query = QUERIES.get(asin, p['title'])
            new_url = make_search_url(query)
            p['affiliateUrl'] = new_url
            changes += 1
            print(f"  {asin} -> {query[:60]}")

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"\nTotal: {changes} /dp/ links converted to search URLs")

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
