"""
add-pros-cons.py
Adds `pros`, `cons`, `whoFor`, and `whoNotFor` fields to product manifests
from existing data like specs, brand, price, and review body.
"""
import json, glob

def generate_pros_cons(product, manifest):
    """Generate pros/cons from product specs + context"""
    pros = []
    cons = []

    title = (product.get('title') or '').lower()
    brand = (product.get('brand') or '').lower()
    specs = product.get('specs', {})
    price = product.get('price', 0)
    rating = product.get('rating', 0)
    cat = (manifest.get('subcategory') or manifest.get('category') or '').lower()

    # From rating
    if rating >= 4.5:
        pros.append(f"Exceptional {rating}-star customer rating")
    elif rating >= 4.0:
        pros.append(f"Strong {rating}-star customer rating")
    else:
        cons.append(f"Only {rating}-star average rating")

    # From price — infer budget vs premium
    if cat == 'blenders':
        if price and price > 300:
            pros.append("Pro-grade motor for tough ingredients")
            cons.append("Premium price point")
        elif price and price < 150:
            pros.append("Excellent value for the price")
            cons.append("Less powerful than premium models")
    elif cat == 'air-fryers':
        if 'dual' in title or '2' in title or 'xl' in title:
            pros.append("Dual-zone cooking for multiple dishes")
            cons.append("Larger footprint on the counter")
        if price and price < 120:
            pros.append("Budget-friendly entry point")
            cons.append("Smaller capacity than larger models")
    elif cat == 'coffee-makers':
        if 'espresso' in title:
            pros.append("Authentic espresso at home")
            cons.append("Learning curve for beginners")
        if 'french' in title or 'press' in title:
            pros.append("No paper filters needed")
            cons.append("Manual operation requires more effort")
    elif cat == 'stand-mixers':
        if 'tilt' in title:
            pros.append("Tilt-head design for easy bowl access")
        if 'bowl-lift' in title:
            pros.append("Bowl-lift mechanism for heavy batches")
        if price and price > 300:
            cons.append("Significant investment for casual bakers")
    elif cat == 'toasters':
        if '4-slice' in title:
            pros.append("Four-slice capacity for families")
        else:
            pros.append("Compact 2-slice footprint")
            cons.append("Limited capacity for families")
    elif cat == 'standing-desks':
        if price and price < 400:
            pros.append("Affordable entry into standing desk world")
            cons.append("Fewer premium features")
        if price and price > 600:
            pros.append("Premium build quality and materials")
            cons.append("Higher investment than competitors")
        if 'frame-only' in title or 'frame' in title:
            pros.append("Use your own desktop for a custom look")

    # Generic spec-based
    if specs:
        for k, v in specs.items():
            k_low = k.lower()
            if 'motor' in k_low or 'hp' in k_low or 'watt' in k_low or 'power' in k_low:
                pros.append(f"Powerful {v} motor")
            if 'weight' in k_low and 'capacity' in k_low:
                try:
                    val = float(str(v).split()[0])
                    if val > 300:
                        pros.append(f"Impressive {v} weight capacity")
                except:
                    pass
            if 'speed' in k_low:
                pros.append(f"{v} speed settings for versatility")

    # Fallback if empty
    if not pros:
        pros.append("Solid build quality for the price")
    if not cons:
        cons.append("May lack premium features of higher-end models")

    return pros[:5], cons[:4]

def generate_who_for(product, manifest):
    """Generate whoFor / whoNotFor from product data"""
    brand = (product.get('brand') or '').lower()
    title = (product.get('title') or '').lower()
    price = product.get('price', 0)
    cat = (manifest.get('subcategory') or manifest.get('category') or '').lower()

    responses = {
        'blenders': {
            'vitamix': ("Home cooks who want pro-grade blending power and don't mind the investment. Ideal for daily smoothies, nut butters, soups, and large batches.",
                        "Budget-conscious shoppers who only blend occasionally. A $50 blender handles basic tasks just fine."),
            'ninja': ("Anyone wanting strong blending performance without the Vitamix price tag. Great for families making smoothies and sauces several times a week.",
                     "Serious cooks who need the longevity and repairability of a commercial-grade machine."),
        },
        'air-fryers': {
            'ninja': ("Busy households cooking for 3-5 people. The dual-basket design is perfect when you need a main dish and a side at the same time.",
                     "Single-person households — the large footprint may be overkill for solo meals."),
            'cosori': ("New air fryer adopters who want a proven, easy-to-use model with a large community and recipe support.",
                      "Cooks who need to prepare multiple dishes simultaneously."),
            'instant-pot': ("Instant Pot fans already in that ecosystem, or anyone with limited counter space who wants an air fryer that does more than just fry.",
                            "Air fryer purists who want maximum frying capacity. The Vortex Plus is a 6-in-1 but trades some capacity for versatility."),
        },
        'coffee-makers': {
            'breville': ("Home baristas serious about espresso who want cafe-quality shots without a $2,000 machine. Great for lattes, cappuccinos, and cortados.",
                         "Drip coffee drinkers who just want a simple pot in the morning."),
            'ninja': ("Households with mixed coffee preferences — one person wants a full carafe, another wants a travel mug. The programmable timer is excellent for morning schedules.",
                     "Espresso purists — this is a drip brewer, not an espresso machine."),
            'hamilton-beach': ("Multi-drink households: one person wants K-Cups, another wants a carafe, another wants a single cup using grounds. The FlexBrew does all three.",
                              "Minimalist coffee drinkers who only want one brewing method — a dedicated machine will be simpler."),
            'bodum': ("Coffee purists who love the ritual and full-bodied flavor of French press brewing. No electricity, no paper waste, and travel-friendly.",
                      "Busy mornings where you need a pot ready on a timer. French press requires active attention and a separate hot water source."),
        },
        'stand-mixers': {
            'kitchenaid': ("Home bakers who bake weekly or more — bread, cakes, cookies, meringues. KitchenAid has the widest attachment ecosystem (pasta, grinding, spiralizing).",
                          "Occasional box-mix bakers — a hand mixer costs a fraction of the price."),
            'cuisinart': ("Bakers who want a powerful mixer with a larger bowl (5.5 qt) at a lower price than comparable KitchenAids. The 800W motor handles stiff doughs well.",
                          "KitchenAid loyalists who already own compatible attachments — Cuisinart uses a different hub design."),
        },
        'toasters': {
            'breville': ("Toast enthusiasts who appreciate 'a bit more' lift for crumpets, bagels, and artisan breads. The die-cast build is stunning on open shelving.",
                         "Budget shoppers — a $30 toaster also makes toast."),
            'cuisinart': ("Technophiles who love the touch-to-toast leverless design and the compact form. The CPT-122 is ideal for small kitchens and solo toasters.",
                          "Large families needing 4-slice throughput every morning."),
            'kitchenaid': ("KitchenAid kitchen ecosystem owners who want a matching toaster. The KMT4117 handles bagels, artisan bread, and gluten-free loaves with excellent evenness.",
                           "Minimalist kitchens where the toaster lives in a cupboard — the KitchenAid is heavy to move around."),
        },
        'standing-desks': {
            'vari': ("Office workers wanting the smoothest, quietest electric motor in a ready-to-assemble package. The ComfortEdge curved front is ergonomically excellent.",
                     "DIY enthusiasts who want maximum customization of frame and desktop separately."),
            'flexispot': ("Value-seeking buyers who still want premium features. The E7 Pro has dual motors and a 355 lb capacity at a mid-tier price.",
                         "Buyers wanting a single-motor budget solution — the E7 Pro is priced above entry-level."),
            'uplift-desk': ("Ergonomic obsessives willing to pay for the best. Uplift has the widest customizability (desktop size, material, color, accessories) and best 15-year warranty.",
                           "Budget buyers — Uplift V2 starts where most competitors' premium options end."),
            'autonomous': ("Clean, minimalist desk buyers who want a modern look without the premium markup. SmartDesk Core is popular with startups and home office setups.",
                          "Users needing accessories like advanced cable management or monitor arms from the same brand — Autonomous has fewer add-ons."),
            'fully-herman-miller': ("Herman Miller design fans who want one of the most stable frames on the market, backed by the brand's legendary warranty and support.",
                                   "Bargain hunters — the Jarvis is now a premium offering since the Herman Miller acquisition."),
            'shw': ("Absolute budget buyers — the SHW is often the cheapest electric standing desk available. Good for students, temporary setups, or trying standing desks for the first time.",
                   "Heavy daily users — the SHW has a lighter motor and thinner desktop. It won't hold up like a FlexiSpot or Uplift over years of heavy use."),
            'fezibo': ("Trendy home office buyers wanting a desk that doesn't look like office furniture. Fezibo offers color options (white, rustic brown, black) many competitors don't.",
                      "Users with heavy monitor setups — check weight capacity carefully as Fezibo's motor is mid-tier."),
        },
    }

    # Find matching category entry
    cat_entries = responses.get(cat, {})
    for key, (who, not_who) in cat_entries.items():
        if key in brand or key in title:
            return who, not_who

    # Category-level generic fallback
    generic = {
        'blenders': ("Home cooks who regularly make smoothies, soups, and sauces and want reliable blending performance.",
                     "Infrequent blender users — an immersion blender may be more practical."),
        'air-fryers': ("Home cooks wanting faster, healthier versions of fried foods without deep-frying mess and oil.",
                       "Those with very limited counter space who can't accommodate another appliance."),
        'coffee-makers': ("Daily coffee drinkers looking for a convenient, reliable brewer at home.",
                          "Espresso-only drinkers who prefer cafe-quality shots."),
        'stand-mixers': ("Regular bakers making cookies, bread, cakes, and meringues who want power and hands-free mixing.",
                         "Occasional bakers — a hand mixer handles most small jobs at a fraction of the price and storage space."),
        'toasters': ("Anyone who wants reliable, even toasting for bread, bagels, and English muffins.",
                     "Rare toaster users — a toaster oven may offer more versatility."),
        'standing-desks': ("Remote workers, office employees, or anyone sitting 6+ hours a day who wants to improve posture, reduce back pain, and boost energy.",
                          "People who rarely sit at a desk or already have a dedicated desk setup they're happy with."),
    }
    return generic.get(cat, ("Buyers looking for a quality product in this category.",
                            "Shoppers with very different needs or budget constraints."))

def main():
    manifest_files = sorted(glob.glob('data/manifests/*.json'))

    for fpath in manifest_files:
        data = json.load(open(fpath))
        modified = False

        for m in data:
            if m['type'] != 'product':
                continue
            for product in m.get('products', []):
                if not product.get('pros'):
                    product['pros'], product['cons'] = generate_pros_cons(product, m)
                    modified = True
                if not product.get('whoFor'):
                    product['whoFor'], product['whoNotFor'] = generate_who_for(product, m)
                    modified = True

        if modified:
            json.dump(data, open(fpath, 'w'), indent=2)
            print(f"Updated {fpath} ({len(data)} manifests)")

    print("\nDone — pros/cons/whoFor/whoNotFor added to all product manifests.")

if __name__ == '__main__':
    main()
