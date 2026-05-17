"""Fetch product images from manufacturer websites."""
import re, subprocess, os, json

os.chdir(r'C:\Users\Eland\.openclaw\workspace\gearcompared')

MANUFACTURER_PAGES = {
    "B07L34K4BH": "https://www.vitamix.com/us/en_us/products/e310",
    "B0BCN28P8G": "https://www.ninjakitchen.com/products/ninja-professional-plus-blender-duo-with-auto-iq-zidBN701",
    "B07GV2SGRD": "https://www.ninjakitchen.com/products/ninja-professional-plus-blender-zidBN701",
    "B0CBSB2L7K": "https://www.ninjakitchen.com/products/ninja-foodi-dualzone-air-fryer-zidDZ201",
    "B0798G41DB": "https://www.ninjakitchen.com/products/ninja-12-cup-programmable-coffee-brewer-zidCE251",
    "B08C76KF7Q": "https://www.hamiltonbeach.com/flexbrew-trio-coffee-maker-49350",
    "B005Z2F9T0": "https://www.kitchenaid.com/countertop-appliances/stand-mixers/tilt-head/p.artisan-series-5-quart-tilt-head-stand-mixer.ksm150ps.html",
    "B08XY4D1P4": "https://www.kitchenaid.com/countertop-appliances/stand-mixers/tilt-head/p.classic-plus-series-4.5-quart-tilt-head-stand-mixer.ksm45.html",
    "B07RTX3D8S": "https://www.cuisinart.com/shopping/appliances/stand-mixers/sm-50/",
    "B08CK7TBP3": "https://www.kitchenaid.com/countertop-appliances/toasters/4-slice/p.4-slice-toaster.kmt4117cu.html",
    "B00005OTWM": "https://www.cuisinart.com/shopping/appliances/toasters/cpt-122/",
}

def fetch_hero_image(url):
    """Fetch page and try to find the main product image."""
    tmp = 'tmp_mfr.html'
    try:
        subprocess.run(['curl.exe', '-sL', '-o', tmp, '-H', 'User-Agent: Mozilla/5.0', url], timeout=15, capture_output=True)
        if not os.path.exists(tmp) or os.path.getsize(tmp) < 500:
            return None
        with open(tmp, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()
        
        # Patterns for manufacturer product hero images
        patterns = [
            r'(?:og:image|twitter:image)\s+content="([^"]+)"',
            r'"(https://[^"]*?(?:hero|product|large)[^"]*?\.(?:jpg|png|webp)[^"]*)"',
            r'data-src="(https://[^"]*?(?:hero|product)[^"]*?\.(?:jpg|png)[^"]*)"',
            r'src="(https://[^"]*?(?:hero|product|zoom)[^"]*?\.(?:jpg|png)[^"]*?)"',
        ]
        
        for pattern in patterns:
            imgs = re.findall(pattern, html, re.IGNORECASE)
            if imgs:
                # Pick the first that seems like a product image
                for img in imgs:
                    if 'icon' not in img.lower() and 'logo' not in img.lower() and 'thumb' not in img.lower():
                        return img
                return imgs[0]
        
        # Fallback: any image with product-like characteristics
        all_imgs = re.findall(r'https://[^"\'\s]+\.(?:jpg|png|webp)', html)
        product_imgs = [i for i in all_imgs if any(k in i.lower() for k in ['product', 'hero', 'large', 'zoom', 'primary']) and not any(b in i.lower() for b in ['icon', 'logo', 'thumb', 'avatar', 'banner'])]
        return product_imgs[0] if product_imgs else None
    
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    with open('data/products/kitchen-appliances.json') as f:
        products = json.load(f)
    
    updated = 0
    for p in products:
        asin = p['asin']
        if 'picsum.photos' not in p.get('imageUrl', ''):
            continue
        if asin not in MANUFACTURER_PAGES:
            continue
        
        url = MANUFACTURER_PAGES[asin]
        print(f"Fetching {asin} ({p['title'][:40]})...", end=' ', flush=True)
        img = fetch_hero_image(url)
        if img:
            p['imageUrl'] = img
            updated += 1
            print(f"OK: {img[:90]}")
            # Save incrementally
            with open('data/products/kitchen-appliances.json', 'w') as f:
                json.dump(products, f, indent=2)
        else:
            print("FAILED")
    
    # Stats
    found = sum(1 for x in products if 'picsum.photos' not in x.get('imageUrl', ''))
    print(f"\nKitchen: {found}/{len(products)} with real images")

if __name__ == '__main__':
    main()
