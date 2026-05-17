"""
Generate clean SVG placeholder images for products without Amazon photos.
Professional-looking, with brand name + product category.
Saves to public/images/products/ and updates product data.
"""
import json, os

os.chdir(r'C:\Users\Eland\.openclaw\workspace\gearcompared')

SVG_TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color1}"/>
      <stop offset="100%" style="stop-color:{color2}"/>
    </linearGradient>
  </defs>
  <rect width="600" height="600" fill="url(#bg)"/>
  <text x="300" y="220" text-anchor="middle" font-family="Georgia, serif" font-size="32" fill="white" font-weight="bold">{brand}</text>
  <text x="300" y="280" text-anchor="middle" font-family="Georgia, serif" font-size="28" fill="rgba(255,255,255,0.9)">{category}</text>
  <text x="300" y="340" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="rgba(255,255,255,0.7)">Product Photo</text>
  <text x="300" y="400" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="rgba(255,255,255,0.5)">Available on Amazon</text>
</svg>'''

BRAND_COLORS = {
    "Vitamix": ("#E31837", "#C41230"),
    "Ninja": ("#1A1A2E", "#16213E"),
    "Breville": ("#C8102E", "#A00D24"),
    "KitchenAid": ("#2D2A6E", "#1B1854"),
    "Cuisinart": ("#D4AF37", "#B8960F"),
    "Hamilton Beach": ("#0077C8", "#005A99"),
    "Instant Pot": ("#00A86B", "#008554"),
    "COSORI": ("#FF6B35", "#E55A2B"),
    "Bodum": ("#2C3E50", "#1A252F"),
    "Vari": ("#4A90D9", "#357ABD"),
    "FlexiSpot": ("#F5A623", "#D4891A"),
    "Uplift": ("#7ED321", "#64B315"),
    "Fully": ("#9B59B6", "#7D3C98"),
    "Autonomous": ("#3498DB", "#2980B9"),
    "SHW": ("#95A5A6", "#7F8C8D"),
    "FEZIBO": ("#E67E22", "#D35400"),
}

CATEGORY_NAMES = {
    "blenders": "Blender",
    "air-fryers": "Air Fryer",
    "coffee-makers": "Coffee Maker",
    "stand-mixers": "Stand Mixer",
    "toasters": "Toaster",
    "standing-desks": "Standing Desk",
}

def get_colors(brand):
    for key, val in BRAND_COLORS.items():
        if key.lower() in brand.lower():
            return val
    return ("#607D8B", "#455A64")  # default slate

def main():
    img_dir = 'public/images/products'
    os.makedirs(img_dir, exist_ok=True)
    
    product_files = [
        'data/products/standing-desks.json',
        'data/products/kitchen-appliances.json',
    ]
    
    generated = 0
    for fpath in product_files:
        with open(fpath) as f:
            products = json.load(f)
        changed = False
        
        for p in products:
            if 'picsum.photos' not in p.get('imageUrl', ''):
                continue
            
            brand = p.get('brand', 'Product')
            cat_key = p.get('subcategory', p.get('category', ''))
            cat_name = CATEGORY_NAMES.get(cat_key, p.get('category', 'Home'))
            c1, c2 = get_colors(brand)
            
            svg = SVG_TEMPLATE.format(
                brand=brand,
                category=cat_name,
                color1=c1,
                color2=c2
            )
            
            filename = f"{p['asin']}.svg"
            filepath = os.path.join(img_dir, filename)
            with open(filepath, 'w') as f_img:
                f_img.write(svg)
            
            p['imageUrl'] = f'/images/products/{filename}'
            changed = True
            generated += 1
            print(f"  {p['asin']} -> /images/products/{filename} ({brand} {cat_name})")
        
        if changed:
            with open(fpath, 'w') as f:
                json.dump(products, f, indent=2)
    
    print(f"\nGenerated {generated} SVG placeholders")

if __name__ == '__main__':
    main()
