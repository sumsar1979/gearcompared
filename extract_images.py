import re, json, gzip

with open('tmp_amz.html', 'rb') as f:
    raw = f.read()

# Try gzip decompress
html = gzip.decompress(raw).decode('utf-8', errors='ignore')

# Pattern: all media-amazon images
imgs = re.findall(r'https://m\.media-amazon\.com/images/I/[^\s"\']+\.jpg', html)
if imgs:
    # Filter for product images (not icons, not sprites)
    product_imgs = [i for i in imgs if 'SY' not in i[:150] and 'SS' not in i[:150] and len(i) > 60]
    if not product_imgs:
        product_imgs = imgs
    print(f"Found {len(product_imgs)} product images")
    for i in product_imgs[:3]:
        print(i[:150])
else:
    # data-old-hires
    imgs = re.findall(r'data-old-hires="(https://[^"]+)"', html)
    if imgs:
        print(f"data-old-hires: {imgs[0][:150]}")
    else:
        imgs = re.findall(r'"large":"(https://m\.media-amazon\.com/images/I/[^"]+)"', html)
        if imgs:
            print(f"large: {imgs[0][:150]}")
        else:
            print("No images found")
            # check for landingImage area
            idx = html.find('landingImage')
            if idx > 0:
                print(html[idx:idx+300])
