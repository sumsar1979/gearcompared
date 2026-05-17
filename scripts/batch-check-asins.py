"""Browser-based ASIN checker via eval on page."""
import json
from pathlib import Path

root = Path(r'C:\Users\Eland\.openclaw\workspace\gearcompared')

all_asins = {}
for fname in ['data/products/standing-desks.json', 'data/products/kitchen-appliances.json']:
    data = json.load(open(root / fname))
    for p in data:
        all_asins[p['asin']] = {
            'title': p['title'],
            'category': Path(fname).stem.replace('-', ' ')
        }

# Dump as JSON for the browser script
print(json.dumps(all_asins, indent=2))
