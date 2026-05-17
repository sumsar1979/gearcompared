"""
Fetch product images from Amazon for all GearCompared products.
Stores the discovered image URLs in the product JSON files.
"""
import json, re, gzip, subprocess, time, sys, os

PRODUCT_FILES = [
    'data/products/standing-desks.json',
    'data/products/kitchen-appliances.json',
]
OUT_DIR = 'public/images/products'
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_image_for_asin(asin):
    """Fetch Amazon page, extract first large product image URL."""
    url = f'https://www.amazon.com/dp/{asin}'
    tmpfile = f'tmp_amz_{asin}.html'
    
    try:
        result = subprocess.run([
            'curl.exe', '-sL', '-o', tmpfile,
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--compressed',
            url
        ], timeout=15, capture_output=True)
        
        if not os.path.exists(tmpfile) or os.path.getsize(tmpfile) < 500:
            return None
        
        with open(tmpfile, 'rb') as f:
            raw = f.read()
        
        # Decompress if gzip
        try:
            html = gzip.decompress(raw).decode('utf-8', errors='ignore')
        except:
            html = raw.decode('utf-8', errors='ignore')
        
        # Find the main product image - prefer landingImage or imgTagWrapper
        patterns = [
            r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+\._AC_SL1500_\.jpg)"',
            r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"',
            r'data-old-hires="(https://[^"]+)"',
            r'https://m\.media-amazon\.com/images/I/[^\s"\']+\._AC_SL1500_\.jpg',
        ]
        
        for pattern in patterns:
            imgs = re.findall(pattern, html)
            if imgs:
                # Filter out icon/sprite images
                for img in imgs:
                    if any(x in img for x in ['_AC_SL1500_', '_SL1500_']):
                        return img
                return imgs[0]  # fallback to first match
        
        return None
    
    finally:
        if os.path.exists(tmpfile):
            os.remove(tmpfile)


def main():
    all_products = []
    for fpath in PRODUCT_FILES:
        with open(fpath) as f:
            products = json.load(f)
        all_products.append((fpath, products))
    
    total = sum(len(ps) for _, ps in all_products)
    print(f"Fetching images for {total} products...\n")
    
    updated = 0
    
    for fpath, products in all_products:
        changed = False
        for i, p in enumerate(products):
            asin = p['asin']
            current_url = p.get('imageUrl', '')
            
            # Skip if already has a real Amazon image
            if 'media-amazon.com' in current_url:
                print(f"  [{i+1}/{total}] {p['title'][:50]}... OK (already has image)")
                continue
            
            print(f"  [{i+1}/{total}] {p['title'][:50]}...", end=' ', flush=True)
            img_url = fetch_image_for_asin(asin)
            
            if img_url:
                p['imageUrl'] = img_url
                changed = True
                updated += 1
                print(f"FOUND: {img_url[:80]}...")
            else:
                print("FAILED (keeping placeholder)")
            
            time.sleep(1.5)  # polite delay
        
        if changed:
            with open(fpath, 'w') as f:
                json.dump(products, f, indent=2)
            print(f"  Saved {fpath}\n")
    
    print(f"\nDone. Updated {updated}/{total} products.")

if __name__ == '__main__':
    main()
