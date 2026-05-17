"""Try Googlebot UA to fetch Amazon images for remaining products."""
import re, gzip, subprocess, os, json, time

os.chdir(r'C:\Users\Eland\.openclaw\workspace\gearcompared')

def fetch_with_googlebot(asin):
    url = f'https://www.amazon.com/dp/{asin}'
    tmp = f'tmp_gb_{asin}.html'
    try:
        subprocess.run([
            'curl.exe', '-sL', '-o', tmp,
            '-H', 'User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            '--compressed', url
        ], timeout=15, capture_output=True)
        
        if not os.path.exists(tmp) or os.path.getsize(tmp) < 500:
            return None
        
        with open(tmp, 'rb') as f:
            raw = f.read()
        try:
            html = gzip.decompress(raw).decode('utf-8', errors='ignore')
        except:
            html = raw.decode('utf-8', errors='ignore')
        
        patterns = [
            r'https://m\.media-amazon\.com/images/I/[^\s\"\']+\._AC_SL1500_\.jpg',
            r'https://m\.media-amazon\.com/images/I/[^\s\"\']+\._SL1500_\.jpg',
        ]
        for pat in patterns:
            imgs = re.findall(pat, html)
            if imgs:
                for img in imgs:
                    if 'SS40' not in img and 'SY' not in img[:150]:
                        return img
                return imgs[0]
        return None
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    with open('data/products/kitchen-appliances.json') as f:
        products = json.load(f)
    
    missing = [p for p in products if 'picsum.photos' in p.get('imageUrl','')]
    print(f"Trying Googlebot UA for {len(missing)} products...")
    
    updated = 0
    for p in missing:
        print(f"  {p['asin']} {p['title'][:50]}...", end=' ', flush=True)
        img = fetch_with_googlebot(p['asin'])
        if img:
            p['imageUrl'] = img
            updated += 1
            with open('data/products/kitchen-appliances.json', 'w') as f:
                json.dump(products, f, indent=2)
            print(f"OK: {img[:80]}")
        else:
            print("FAIL")
        time.sleep(1)
    
    found = sum(1 for x in products if 'picsum.photos' not in x.get('imageUrl',''))
    print(f"\nKitchen: {found}/{len(products)} with real images")

if __name__ == '__main__':
    main()
