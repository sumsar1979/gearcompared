import json
for cat in ['standing-desks', 'kitchen-appliances']:
    with open(f'data/products/{cat}.json') as f:
        data = json.load(f)
    for p in data:
        url = p.get('affiliateUrl','')
        lt = 'dp' if '/dp/' in url else ('search' if '/s?' in url else 'OTHER')
        if lt != 'dp':
            print(f'[{lt}] {p["asin"]} - {p["title"][:55]}')
