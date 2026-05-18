"""
Batch verify all untested ASINs via browser, one by one.
This is slow but reliable. Run inline.
"""
import json

# Load all products
products = []
for cat in ['standing-desks', 'kitchen-appliances']:
    with open(f'C:\\Users\\Eland\\.openclaw\\workspace\\gearcompared\\data\\products\\{cat}.json') as f:
        products.extend(json.load(f))

confirmed_live = {'B0CT95J8XH','B0B422BBHT','B08572G1FG','B07SZHWCH5','B008H4SLV6'}
confirmed_dead = {'B08CK7TBP3','B00005OTWM','B07L34K4BH','B0BCN28P8G','B0DHS5X6WD','B005Z2F9T0'}

untested = [p for p in products if p['asin'] not in confirmed_live and p['asin'] not in confirmed_dead]

# Print as a list for easy reference
for i, p in enumerate(untested):
    print(f"{i}: {p['asin']} | {p['title'][:60]}")
