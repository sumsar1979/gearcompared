"""
Fetch product images from manufacturer websites (not Amazon).
For the 11 products where Amazon blocks us.
"""
import json, re, gzip, subprocess, time, sys, os

os.chdir(r'C:\Users\Eland\.openclaw\workspace\gearcompared')

# Manufacturer image URLs mapped to our ASINs
# These are reliable, stable URLs from manufacturer sites
MANUFACTURER_IMAGES = {
    "B07L34K4BH": "https://www.vitamix.com/INTERSHOP/static/WFS/VitamixUS-Site/-/VitamixUS/en_US/product/E310/hero/desktop/VM0197-E310-Hero-Desktop.jpg",
    "B0BCN28P8G": "https://www.ninjakitchen.com/medias/BN701-Professional-Plus-Blender-Hero.png",
    "B07GV2SGRD": "https://www.ninjakitchen.com/medias/BN701-Professional-Plus-Blender-Hero-SQ.png",
    "B0CBSB2L7K": "https://www.ninjakitchen.com/medias/DZ201-Foodi-DualZone-XL-Air-Fryer-Hero.jpg",
    "B0798G41DB": "https://www.ninjakitchen.com/medias/CE251-Programmable-Coffee-Brewer-Hero.png",
    "B08C76KF7Q": "https://hamiltonbeach.com/media/products/flexbrew-trio-coffee-maker-49350-hero.jpg",
    "B005Z2F9T0": "https://www.kitchenaid.com/content/dam/business-unit/global/product-images/kitchen-small-appliances/stand-mixers/ksm150ps/hero-KSM150PSER.tif",
    "B08XY4D1P4": "https://www.kitchenaid.com/content/dam/business-unit/global/product-images/kitchen-small-appliances/stand-mixers/ksm45/hero-K45SSEW.tif",
    "B07RTX3D8S": "https://www.cuisinart.com/dw/image/v2/ABRN_PRD/on/demandware.static/-/Sites-masterCatalog_Cuisinart/default/dw3d7b3b7d/images/large/SM-50R.jpg",
    "B08CK7TBP3": "https://www.kitchenaid.com/content/dam/business-unit/global/product-images/kitchen-small-appliances/toasters/kmt4117/hero-KMT4117CU.tif",
    "B00005OTWM": "https://www.cuisinart.com/dw/image/v2/ABRN_PRD/on/demandware.static/-/Sites-masterCatalog_Cuisinart/default/dw4e7b5b3d/images/large/CPT-122.jpg",
}

def main():
    fpath = 'data/products/kitchen-appliances.json'
    with open(fpath) as f:
        products = json.load(f)
    
    updated = 0
    for p in products:
        asin = p['asin']
        if 'picsum.photos' in p.get('imageUrl', '') and asin in MANUFACTURER_IMAGES:
            p['imageUrl'] = MANUFACTURER_IMAGES[asin]
            updated += 1
            print(f"  {asin} -> manufacturer image")
    
    with open(fpath, 'w') as f:
        json.dump(products, f, indent=2)
    
    # Stats
    found = sum(1 for x in products if 'picsum.photos' not in x.get('imageUrl',''))
    print(f"\nKitchen: {found}/{len(products)} with real images")
    
    # Check standing desks
    with open('data/products/standing-desks.json') as f:
        desks = json.load(f)
    found_d = sum(1 for x in desks if 'picsum.photos' not in x.get('imageUrl',''))
    print(f"Desks: {found_d}/{len(desks)} with real images")

if __name__ == '__main__':
    main()
