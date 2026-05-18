import json, glob

all_pages = []
for f in sorted(glob.glob('data/manifests/*.json')):
    data = json.load(open(f))
    for m in data:
        all_pages.append({
            'type': m['type'],
            'slug': m['slug'],
            'category': m.get('category', ''),
            'subcategory': m.get('subcategory', '') or '',
            'title': m.get('title', ''),
            'products': [p.get('title', '') for p in m.get('products', [])],
        })

# Print manifest
for p in all_pages:
    print(f"{p['type']:12s} | {p['category']:25s} | {p['subcategory']:20s} | {p['slug']}")

# Count by type
from collections import Counter
print("\n--- Counts ---")
for t, c in Counter(p['type'] for p in all_pages).items():
    print(f"  {t}: {c}")
print(f"  Total: {len(all_pages)}")
