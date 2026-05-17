"""Check all ASINs one by one via browser and report dead links."""
import json, asyncio

# Output from manual browser verification
from pathlib import Path
root = Path(r'C:\Users\Eland\.openclaw\workspace\gearcompared')

all_asins = {}
for fname in ['data/products/standing-desks.json', 'data/products/kitchen-appliances.json']:
    data = json.load(open(root / fname))
    for p in data:
        all_asins[p['asin']] = p['title']

# Already verified manually:
verified_dead = ['B07L34K4BH']  # Vitamix E310 - dog page
verified_live = ['B008H4SLV6']  # Vitamix 5200 - live

print("ALL ASINS TO CHECK (30 total):")
for asin, title in all_asins.items():
    status = 'DEAD' if asin in verified_dead else ('LIVE' if asin in verified_live else 'UNKNOWN')
    print(f"  {status:8s} {asin} - {title[:60]}")

print(f"\nKnown dead: {len(verified_dead)}/{len(all_asins)}")
print(f"Known live: {len(verified_live)}/{len(all_asins)}")
print(f"Unknown: {len(all_asins) - len(verified_dead) - len(verified_live)}")
