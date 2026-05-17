"""
Fetch product images from Amazon - robust incremental version.
Saves after each product so progress is never lost.
"""
import json, re, gzip, subprocess, time, sys, os

os.chdir(r'C:\Users\Eland\.openclaw\workspace\gearcompared')

PRODUCT_FILES = [
    'data/products/standing-desks.json',
    'data/products/kitchen-appliances.json',
]

def fetch_image(asin):
    url = f'https://www.amazon.com/dp/{asin}'
    tmpfile = f'tmp_amz_{asin}.html'
    
    try:
        subprocess.run([
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
                    if any(x in img for x in ['_SS40_', '_SY', 'sprite', 'pixel', 'transparent']):
                        continue
                    return img
                return imgs[0]
        
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
    print(f"Fetching images for {total} products...")
    
    for fpath, products in all_products:
        for p in products:
            asin = p['asin']
            current = p.get('imageUrl', '')
            
            if 'media-amazon.com' in current:
                print(f"  SKIP {asin} (already has image)")
                continue
            
            sys.stdout.write(f"  FETCH {asin} ... ")
            sys.stdout.flush()
            
            img = fetch_image(asin)
            if img:
                p['imageUrl'] = img
                # Save immediately
                with open(fpath, 'w') as f:
                    json.dump(products, f, indent=2)
                print(f"OK: {img[:80]}")
            else:
                print("FAIL")
            
            time.sleep(2)
    
    # Final stats
    for fpath, products in all_products:
        with open(fpath) as f:
            p = json.load(f)
        found = sum(1 for x in p if 'media-amazon' in x.get('imageUrl',''))
        print(f"  {fpath}: {found}/{len(p)} with real images")

if __name__ == '__main__':
    main()
