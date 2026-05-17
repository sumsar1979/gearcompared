import json

for fname in ['standing-desks', 'kitchen-appliances']:
    with open(f'data/manifests/{fname}.json') as f:
        manifests = json.load(f)
    for m in manifests:
        if m['type'] == 'product':
            p = m['products'][0]
            body = m.get('body', '')
            print(f"{p['title']}: body={len(body)} chars")
