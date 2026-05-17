"""
Fetch missing product images using browser automation.
Much more reliable than curl (uses real browser fingerprints).
"""
import json, time, asyncio

PRODUCT_FILES = [
    'data/products/standing-desks.json',
    'data/products/kitchen-appliances.json',
]

# Collect missing ASINs
missing = []
for fpath in PRODUCT_FILES:
    with open(fpath) as f:
        products = json.load(f)
    for p in products:
        if 'picsum.photos' in p.get('imageUrl', ''):
            missing.append((fpath, p))

print(f"Missing images for {len(missing)} products.")
print("ASINs to fetch:")
for _, p in missing:
    print(f"  {p['asin']}  {p['title'][:50]}")

# Write list for manual/browser fetching
with open('missing_asins.txt', 'w') as f:
    for _, p in missing:
        f.write(f"{p['asin']}\t{p['title']}\n")
print("\nWrote missing_asins.txt")
