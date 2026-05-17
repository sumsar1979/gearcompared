"""
Retry fetching images for products that still have placeholder imageUrls.
"""
import json, re, gzip, subprocess, time, os

PRODUCT_FILES = [
    'data/products/standing-desks.json',
    'data/products/kitchen-appliances.json',
]

def fetch_image_for_asin(asin):
    url = f'https://www.amazon.com/dp/{asin}'
    tmpfile = f'tmp_amz_{asin}.html'
    
    try:
        result = subprocess.run([
            'curl.exe', '-sL', '-o', tmpfile,
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            '-H', 'Accept-Language: en-US,en;q=0.9',
            '--compressed',
            url
        ], timeout=20, capture_output=True)
        
        if not os.path.exists(tmpfile) or os.path.getsize(tmpfile) < 500:
            return None
        
        with open(tmpfile, 'rb') as f:
            raw = f.read()
        
        try:
            html = gzip.decompress(raw).decode('utf-8', errors='ignore')
        except:
            html = raw.decode('utf-8', errors='ignore')
        
        patterns = [
            r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+\._AC_SL1500_\.jpg)"',
            r'"hiRes":"(https://m\.media-amazon\.com/images/I/[^"]+)"',
            r'data-old-hires="(https://[^"]+)"',
            r'(https://m\.media-amazon\.com/images/I/[^\s"\']+\._AC_SL1500_\.jpg)',
            r'(https://m\.media-amazon\.com/images/I/[^\s"\']+\._SL1500_\.jpg)',
            r'(https://m\.media-amazon\.com/images/I/[^\s"\']+\._AC_SL[0-9]+_\.jpg)',
        ]
        
        for pattern in patterns:
            imgs = re.findall(pattern, html)
            if imgs:
                for img in imgs:
                    # Skip tiny thumbnails/icons
                    if any(x in img for x in ['_SS40_', '_SY', 'sprite', 'pixel', 'transparent']):
                        continue
                    return img
                return imgs[0]
        
        return None
    
    finally:
        if os.path.exists(tmpfile):
            os.remove(tmpfile)


all_products = []
for fpath in PRODUCT_FILES:
    with open(fpath) as f:
        products = json.load(f)
    all_products.append((fpath, products))

total_missing = sum(1 for _, ps in all_products for p in ps if 'picsum.photos' in p.get('imageUrl',''))
print(f"Retrying {total_missing} products with placeholder images...\n")

updated = 0
idx = 0

for fpath, products in all_products:
    changed = False
    for p in products:
        if 'picsum.photos' not in p.get('imageUrl', ''):
            continue
        idx += 1
        asin = p['asin']
        print(f"  [{idx}/{total_missing}] {p['title'][:55]}...", end=' ', flush=True)
        img_url = fetch_image_for_asin(asin)
        
        if img_url:
            p['imageUrl'] = img_url
            changed = True
            updated += 1
            print(f"OK: {img_url[:80]}...")
        else:
            print("FAILED")
        
        time.sleep(3)  # longer delay for retries
    
    if changed:
        with open(fpath, 'w') as f:
            json.dump(products, f, indent=2)
        print(f"  Saved {fpath}\n")

print(f"\nRetry done. Fixed {updated}/{total_missing}.")
