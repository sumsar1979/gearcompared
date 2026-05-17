#!/usr/bin/env python3
"""
fetch-products.py — Product data pipeline for GearCompared.
Fetches product data (mock or real Amazon PAAPI) and writes to data/products/.
"""

import json
import os
import sys
import random
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "products"
CONFIG_PATH = SCRIPT_DIR / "config.json"

# ─── Mock data generators ────────────────────────────────────

STANDING_DESK_BRANDS = ["Uplift", "Fully", "FlexiSpot", "Vari", "Autonomous", "ApexDesk", "SHW", "FEZIBO"]
STANDING_DESK_MODELS = ["V2", "Pro", "ELX", "L-Shaped", "Essential", "Core", "Elite", "SmartDesk", "Jarvis", "Stand Up"]
STANDING_DESK_SPECS = {
    "Height Range": ['27" - 45"', '25.5" - 51"', '28" - 47.5"', '24" - 50"', '29" - 48"'],
    "Weight Capacity": ["350 lbs", "300 lbs", "275 lbs", "250 lbs", "200 lbs", "355 lbs", "150 lbs"],
    "Desktop Size": ['60" x 30"', '48" x 24"', '55" x 28"', '72" x 30"', '48" x 30"', '60" x 24"'],
    "Material": ["Bamboo", "Walnut", "Oak", "White Laminate", "Black Laminate", "Reclaimed Wood"],
    "Motor Type": ["Dual Motor", "Single Motor", "Crank", "Pneumatic"],
    "RPM": ["High", "Medium", "Standard", "Quiet-Drive"],
}

KITCHEN_BRANDS = ["KitchenAid", "Ninja", "Instant Pot", "Cuisinart", "Breville", "Vitamix", "Hamilton Beach", "De'Longhi"]
KITCHEN_TYPES = {
    "blenders": ["Professional Blender", "Personal Blender", "Immersion Blender", "Food Processor Combo"],
    "air-fryers": ["Dual Basket Air Fryer", "Compact Air Fryer", "Toaster Oven Air Fryer", "XL Air Fryer"],
    "coffee-makers": ["Espresso Machine", "Drip Coffee Maker", "Pour-Over", "Single Serve"],
    "stand-mixers": ["Tilt-Head Stand Mixer", "Bowl-Lift Stand Mixer", "Mini Stand Mixer"],
    "toasters": ["4-Slice Toaster", "2-Slice Toaster", "Smart Toaster", "Toaster Oven"],
}
KITCHEN_SPECS = {
    "blenders": {"Motor Power": ["1200W", "1500W", "1000W", "800W"], "Capacity": ["72 oz", "64 oz", "48 oz", "32 oz"], "Speed Settings": ["10", "6", "5", "3", "Variable"]},
    "air-fryers": {"Capacity": ["8 qt", "6 qt", "5 qt", "4 qt", "10 qt"], "Wattage": ["1700W", "1500W", "1400W", "1200W"], "Functions": ["8-in-1", "10-in-1", "7-in-1", "Air Fry only"]},
    "coffee-makers": {"Brew Size": ["12 cup", "10 cup", "8 cup", "Single serve"], "Bar Pressure": ["15 bar", "19 bar", "9 bar"], "Grinder": ["Built-in", "None"]},
    "stand-mixers": {"Bowl Size": ["5 qt", "6 qt", "7 qt", "4.5 qt"], "Motor Wattage": ["575W", "500W", "300W", "350W"], "Attachments": ["10", "7", "5", "3"]},
    "toasters": {"Slots": ["4", "2", "2 long slot"], "Settings": ["7 shade", "6 shade", "Digital", "Bagel/Defrost"], "Material": ["Stainless Steel", "Brushed Metal", "Retro"]},
}

FEATURES_POOL = {
    "standing-desks": [
        "Electric height adjustment with memory presets",
        "Anti-collision technology",
        "Cable management tray included",
        "Programmable height settings",
        "Spill-resistant surface coating",
        "Whisper-quiet motor operation",
        "Quick 10-minute assembly",
        "LED display with height readout",
        "Integrated USB charging ports",
        "Ergonomic curved front edge",
        "Adjustable leveling feet",
        "15-year warranty on frame",
        "Child lock safety feature",
        "Crossbar for extra stability",
    ],
    "kitchen-appliances": [
        "Dishwasher-safe parts",
        "BPA-free materials",
        "Digital touchscreen controls",
        "Auto-shutoff safety feature",
        "Recipe book included",
        "One-touch presets",
        "Extra-large capacity",
        "Quiet operation technology",
        "Overheat protection",
        "Cord storage in base",
        "Non-slip feet",
        "LED indicator lights",
        "Cool-touch exterior",
        "Multi-function versatility",
    ],
}

def generate_mock_product(asin, category, subcategory=None):
    """Generate realistic fake product data"""
    seed = hash(asin) % 1000
    rng = random.Random(seed)

    if category == "standing-desks":
        brand = rng.choice(STANDING_DESK_BRANDS)
        model = rng.choice(STANDING_DESK_MODELS)
        title = f"{brand} {model} Standing Desk"
        specs = {}
        for key, choices in STANDING_DESK_SPECS.items():
            specs[key] = rng.choice(choices)
        features = rng.sample(FEATURES_POOL["standing-desks"], k=min(5, rng.randint(3, 6)))
        price = round(rng.uniform(199, 899), 2)
        list_price = round(price * rng.uniform(1.1, 1.5), 2) if rng.random() > 0.4 else None
        rating = round(rng.uniform(3.8, 4.9), 1)
        review_count = rng.randint(120, 12500)
        image_id = rng.randint(1, 100)
        image_url = f"https://picsum.photos/seed/{asin}/600/600"

    else:  # kitchen-appliances
        sub = subcategory or rng.choice(list(KITCHEN_TYPES.keys()))
        brand = rng.choice(KITCHEN_BRANDS)
        model_type = rng.choice(KITCHEN_TYPES[sub])
        title = f"{brand} {model_type}"
        specs = {}
        type_specs = KITCHEN_SPECS.get(sub, {})
        for key, choices in type_specs.items():
            specs[key] = rng.choice(choices)
        features = rng.sample(["Dishwasher-safe parts", "BPA-free materials", "Digital touchscreen controls",
            "Auto-shutoff safety feature", "Recipe book included", "One-touch presets", "Extra-large capacity",
            "Quiet operation technology", "Overheat protection", "Cord storage in base", "Non-slip feet",
            "LED indicator lights", "Cool-touch exterior", "Multi-function versatility"],
            k=min(5, rng.randint(3, 6)))
        price = round(rng.uniform(29, 499), 2)
        list_price = round(price * rng.uniform(1.1, 1.6), 2) if rng.random() > 0.4 else None
        rating = round(rng.uniform(3.5, 4.9), 1)
        review_count = rng.randint(200, 28000)
        image_url = f"https://picsum.photos/seed/{asin}/600/600"

    return {
        "asin": asin,
        "title": title,
        "brand": brand,
        "category": category,
        "subcategory": subcategory if category == "kitchen-appliances" else None,
        "price": price,
        "listPrice": list_price,
        "rating": rating,
        "reviewCount": review_count,
        "imageUrl": image_url,
        "specs": specs,
        "features": features,
        "affiliateUrl": f"https://www.amazon.com/dp/{asin}?tag=gearcompared-20",
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
    }


def load_config():
    """Load product ASIN config"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return None


def fetch_products_mock():
    """Generate mock product data for all categories"""
    mock_products = {
        "standing-desks": [],
        "kitchen-appliances": [],
    }

    # Generate 10 standing desks
    for i in range(10):
        asin = f"B0000TEST{i:03d}"
        product = generate_mock_product(asin, "standing-desks")
        mock_products["standing-desks"].append(product)

    # Generate 10 kitchen appliances (2 per subcategory)
    kitchen_subs = ["blenders", "air-fryers", "coffee-makers", "stand-mixers", "toasters"]
    for idx, sub in enumerate(kitchen_subs):
        for j in range(2):
            asin = f"B1000TEST{(idx * 2 + j):03d}"
            product = generate_mock_product(asin, "kitchen-appliances", sub)
            mock_products["kitchen-appliances"].append(product)

    return mock_products


def save_products(products_by_category):
    """Write product JSON to data directory"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for category, products in products_by_category.items():
        filepath = DATA_DIR / f"{category}.json"
        with open(filepath, "w") as f:
            json.dump(products, f, indent=2)
        print(f"  [OK] Wrote {len(products)} products to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="Fetch product data for GearCompared")
    parser.add_argument("--mock", action="store_true", help="Generate mock product data")
    parser.add_argument("--config", type=str, help="Path to product ASIN config JSON")
    args = parser.parse_args()

    print("[GearCompared] Product Fetcher")
    print(f"   Data directory: {DATA_DIR}")

    if args.mock:
        print("   Mode: Mock data generation")
        products = fetch_products_mock()
        save_products(products)
        print("[OK] Mock product data generated successfully!")
        return 0

    if args.config:
        config = load_config() or json.loads(open(args.config).read() if Path(args.config).exists() else "{}")
    else:
        config = load_config()

    if not config:
        print("[WARN] No config found. Run with --mock to generate test data.")
        return 1

    # Real PAAPI fetch would go here
    print("   Mode: Real PAAPI (not yet implemented)")
    print("   Run with --mock for testing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
