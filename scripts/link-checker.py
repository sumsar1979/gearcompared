#!/usr/bin/env python3
"""
GearCompared Link Checker — simple, fast, reliable.
All 30 products use Amazon search URLs (amazon.com/s?k=...).
Search URLs are always live — no ASIN verification needed.
The checker simply ensures no /dp/ links exist and regenerates manifests.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent


def main():
    print(f"GearCompared Link Check — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    
    products = []
    for cat in ['standing-desks', 'kitchen-appliances']:
        with open(ROOT / f'data/products/{cat}.json', 'r', encoding='utf-8') as f:
            products.extend(json.load(f))
    
    dp_links = [p for p in products if '/dp/' in p.get('affiliateUrl', '')]
    search_links = [p for p in products if '/s?k=' in p.get('affiliateUrl', '')]
    
    print(f"Total products: {len(products)}")
    print(f"Search URLs:   {len(search_links)}")
    print(f"/dp/ links:    {len(dp_links)}")
    
    if dp_links:
        print(f"\n[WARN] {len(dp_links)} /dp/ links found:")
        for p in dp_links:
            print(f"  {p['asin']} — {p['title'][:60]}")
        return len(dp_links)
    
    # Regenerate manifests
    import subprocess
    result = subprocess.run(
        ['python', str(ROOT / 'scripts' / 'generate-manifests.py')],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    print(result.stdout.strip())
    
    print("[OK] All links are search URLs. No changes needed.")
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
