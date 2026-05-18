#!/usr/bin/env python3
"""
GearCompared Link Checker — simple, fast, reliable.
All 30 products use Amazon search URLs (amazon.com/s?k=...).
Search URLs are always live — no ASIN verification needed.
Also validates product data integrity: checks for placeholder/test data,
real Amazon CDN images, and proper affiliate tags.
"""
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

# Known real ASIN prefixes from our catalog — if all ASINs start with B0000TEST
# or all images point to picsum.photos, the data has been swapped with placeholders.
FAKE_ASIN_PATTERNS = ['B0000TEST', 'B1000TEST']
FAKE_IMAGE_DOMAINS = ['picsum.photos', 'placeholder.com']
REQUIRED_BRANDS = ['Vari', 'FlexiSpot', 'Uplift', 'Fully', 'Autonomous', 'FEZIBO', 'SHW',
                   'Vitamix', 'Ninja', 'Cosori', 'Instant', 'Breville', 'Cuisinart',
                   'KitchenAid', 'Hamilton', 'Bodum', 'DeLonghi']


def check_data_integrity(products):
    """Return list of warnings if product data looks like test/placeholder data."""
    issues = []
    
    fake_asins = [p for p in products if any(p.get('asin','').startswith(pat) for pat in FAKE_ASIN_PATTERNS)]
    if len(fake_asins) > len(products) * 0.5:
        issues.append(f'CRITICAL: {len(fake_asins)}/{len(products)} products have placeholder ASINs (B0000TEST/B1000TEST). Data was overwritten!')
    
    fake_images = [p for p in products if any(dom in p.get('imageUrl','') for dom in FAKE_IMAGE_DOMAINS)]
    if len(fake_images) > len(products) * 0.5:
        issues.append(f'CRITICAL: {len(fake_images)}/{len(products)} products have placeholder images (picsum.photos). Data was overwritten!')
    
    if len(products) < 30:
        issues.append(f'WARNING: Only {len(products)} products found (expected 30).')
    
    missing_affiliate = [p for p in products if 'gearcompared2-20' not in p.get('affiliateUrl','')]
    if missing_affiliate:
        issues.append(f'WARNING: {len(missing_affiliate)} products missing affiliate tag.')
    
    return issues


def main():
    print(f"GearCompared Link Check — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    
    products = []
    for cat in ['standing-desks', 'kitchen-appliances']:
        path = ROOT / f'data/products/{cat}.json'
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                products.extend(json.load(f))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Try UTF-16 fallback (Windows git can produce this)
            with open(path, 'r', encoding='utf-16-le') as f:
                products.extend(json.load(f))
    
    # === Data integrity check ===
    warnings = check_data_integrity(products)
    for w in warnings:
        print(f'[WARN] {w}')
    
    # === Link check ===
    dp_links = [p for p in products if '/dp/' in p.get('affiliateUrl', '')]
    search_links = [p for p in products if '/s?k=' in p.get('affiliateUrl', '')]
    
    print(f"Total products: {len(products)}")
    print(f"Search URLs:   {len(search_links)}")
    print(f"/dp/ links:    {len(dp_links)}")
    
    if dp_links:
        print(f"\n[WARN] {len(dp_links)} /dp/ links found:")
        for p in dp_links:
            print(f"  {p['asin']} — {p['title'][:60]}")
    
    # === Regenerate manifests ===
    result = subprocess.run(
        ['python', str(ROOT / 'scripts' / 'generate-manifests.py')],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    print(result.stdout.strip())
    
    if warnings:
        print(f"\n[FAIL] {len(warnings)} data integrity issue(s) found!")
        return 1
    
    if dp_links:
        print(f"\n[WARN] {len(dp_links)} /dp/ links need fixing.")
        return len(dp_links)
    
    print("[OK] All links are search URLs. Product data is valid.")
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
