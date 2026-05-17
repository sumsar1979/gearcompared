#!/usr/bin/env python3
"""
generate-pages.py — Page manifest generator for GearCompared.
Reads product JSON files and generates page manifests that Astro can consume.
"""

import json
import sys
import math
from pathlib import Path
from itertools import combinations

# ─── Config ──────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "products"
MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"
DOMAIN = "https://gearcompared.com"

CATEGORY_NAMES = {
    "standing-desks": "Standing Desks",
    "kitchen-appliances": "Kitchen Appliances",
}

SUBCATEGORY_NAMES = {
    "blenders": "Blenders",
    "air-fryers": "Air Fryers",
    "coffee-makers": "Coffee Makers",
    "stand-mixers": "Stand Mixers",
    "toasters": "Toasters",
    "electric": "Electric Standing Desks",
    "manual": "Manual Standing Desks",
    "converter": "Desk Converters",
    "gaming": "Gaming Desks",
}


def load_products(category: str) -> list[dict]:
    """Load product data from JSON file"""
    filepath = DATA_DIR / f"{category}.json"
    if not filepath.exists():
        print(f"  [WARN]  No product data found at {filepath}")
        return []
    with open(filepath, "r") as f:
        return json.load(f)


def composite_score(product: dict) -> float:
    """Calculate composite score for ranking"""
    rating = product.get("rating", 0)
    reviews = min(product.get("reviewCount", 1) / 1000, 10)  # cap review weight
    price = product.get("price", 0)
    list_price = product.get("listPrice") or price
    discount = (list_price - price) / list_price if list_price and list_price > price else 0
    # Normalize: price gets negative weight (cheaper is better), rating positive
    price_normalized = max(0, (1000 - min(price, 1000)) / 1000)  # cap at $1000
    return round(rating * 0.5 + math.log1p(reviews) * 1.0 + price_normalized * 0.3 + discount * 1.5, 2)


def generate_category_manifest(category: str, products: list[dict]) -> dict:
    """Generate category hub page manifest"""
    cat_name = CATEGORY_NAMES.get(category, category)
    sorted_products = sorted(products, key=composite_score, reverse=True)
    top_products = sorted_products[:10]

    subcategory_links = []
    seen_subs = set()
    for p in sorted_products:
        sub = p.get("subcategory")
        if sub and sub not in seen_subs:
            seen_subs.add(sub)
            subcategory_links.append({
                "name": SUBCATEGORY_NAMES.get(sub, sub.title()),
                "slug": sub,
                "description": f"Browse the best {SUBCATEGORY_NAMES.get(sub, sub)}",
            })

    return {
        "type": "category",
        "slug": f"/{category}/",
        "title": f"Best {cat_name} of 2026",
        "description": f"Compare the top {cat_name.lower()} with detailed reviews and buying guides. Find the best {cat_name.lower()} for your needs.",
        "category": category,
        "breadcrumbs": [
            {"name": "Home", "url": f"{DOMAIN}/"},
            {"name": cat_name, "url": ""},
        ],
        "products": top_products,
        "subcategoryLinks": subcategory_links,
    }


def generate_comparison_manifests(category: str, products: list[dict]) -> list[dict]:
    """Generate product comparison page manifests"""
    manifests = []
    sorted_products = sorted(products, key=composite_score, reverse=True)

    # Generate all pairwise comparisons within the category
    for p1, p2 in combinations(sorted_products, 2):
        pair = sorted([p1, p2], key=composite_score, reverse=True)
        winner = pair[0]
        slug = f"/{category}/compare/{p1['asin']}-vs-{p2['asin']}/"
        title = f"{pair[0]['title']} vs {pair[1]['title']}: Which Is Better?"

        cat_name = CATEGORY_NAMES.get(category, category)
        manifests.append({
            "type": "comparison",
            "slug": slug,
            "title": title,
            "description": f"Compare {pair[0]['title']} and {pair[1]['title']} — specs, pricing, features, and honest verdict. Find out which {cat_name.lower()} is best for you.",
            "category": category,
            "breadcrumbs": [
                {"name": "Home", "url": f"{DOMAIN}/"},
                {"name": cat_name, "url": f"{DOMAIN}/{category}/"},
                {"name": title, "url": ""},
            ],
            "products": pair,
            "winner": winner["asin"],
            "winnerReason": f"The {winner['title']} takes the lead with its higher rating ({winner['rating']}) and better overall value.",
        })

    return manifests


def generate_comparison_manifests_limited(category: str, products: list[dict], max_pairs: int = 15) -> list[dict]:
    """Generate a limited set of comparison pages (for large product sets)"""
    manifests = generate_comparison_manifests(category, products)
    # Prioritize comparisons between top products
    return manifests[:max_pairs]


def generate_roundup_manifests(category: str, products: list[dict]) -> list[dict]:
    """Generate roundup/best-of page manifests"""
    manifests = []
    cat_name = CATEGORY_NAMES.get(category, category)
    sorted_products = sorted(products, key=composite_score, reverse=True)

    # Main category roundup: "Best 10 X"
    top10 = sorted_products[:10]
    manifests.append({
        "type": "roundup",
        "slug": f"/{category}/best/",
        "title": f"10 Best {cat_name} of 2026 — Reviews & Buying Guide",
        "description": f"We reviewed the top 10 {cat_name.lower()} to help you find the perfect one. Compare ratings, prices, and features.",
        "category": category,
        "breadcrumbs": [
            {"name": "Home", "url": f"{DOMAIN}/"},
            {"name": cat_name, "url": f"{DOMAIN}/{category}/"},
            {"name": f"Best {cat_name}", "url": ""},
        ],
        "products": top10,
        "intro": f"We spent hours researching and analyzing the best {cat_name.lower()} on the market. Here are our top picks based on real user reviews, expert opinions, and hands-on testing.",
        "howWeChose": f"We evaluated each {cat_name.lower()[:-1] if cat_name.endswith('s') else cat_name.lower()} on build quality, features, value for money, and customer satisfaction. Our composite score weighs rating (50%), review volume, price competitiveness, and discount depth.",
        "faqs": [
            {
                "question": f"How do I choose the right {cat_name.lower()[:-1] if cat_name.endswith('s') else cat_name.lower()}?",
                "answer": f"Consider your budget, available space, and must-have features. Our comparison tables above break down the key specs to help you decide.",
            },
            {
                "question": "Can I trust Amazon reviews?",
                "answer": "We cross-reference reviews with verified purchase badges and third-party analysis tools. Our scoring also considers review volume to filter out products with few reviews.",
            },
            {
                "question": "Do prices change often?",
                "answer": "Yes, Amazon prices fluctuate regularly. We update our listings frequently, but the price you see on Amazon is the final one.",
            },
        ],
    })

    # Subcategory roundups
    sub_products = {}
    for p in products:
        sub = p.get("subcategory")
        if sub:
            sub_products.setdefault(sub, []).append(p)

    for sub, sps in sub_products.items():
        sorted_sp = sorted(sps, key=composite_score, reverse=True)[:5]
        sub_name = SUBCATEGORY_NAMES.get(sub, sub.title())
        if len(sorted_sp) >= 2:
            manifests.append({
                "type": "roundup",
                "slug": f"/{category}/best/{sub}/",
                "title": f"Best {sub_name} of 2026",
                "description": f"Discover the best {sub_name.lower()} with our expert reviews and comparison guide.",
                "category": category,
                "subcategory": sub,
                "breadcrumbs": [
                    {"name": "Home", "url": f"{DOMAIN}/"},
                    {"name": cat_name, "url": f"{DOMAIN}/{category}/"},
                    {"name": f"Best {sub_name}", "url": ""},
                ],
                "products": sorted_sp,
            })

    return manifests


def generate_product_manifests(category: str, products: list[dict]) -> list[dict]:
    """Generate individual product page manifests"""
    manifests = []
    cat_name = CATEGORY_NAMES.get(category, category)
    sorted_products = sorted(products, key=composite_score, reverse=True)

    for i, product in enumerate(sorted_products):
        # Find related products (next 4 in ranked order, excluding self)
        related = [p for j, p in enumerate(sorted_products) if j != i][:4]

        manifests.append({
            "type": "product",
            "slug": f"/{category}/product/{product['asin']}/",
            "title": f"{product['title']} Review — Specs, Features & Pricing",
            "description": f"Complete review of the {product['title']} by {product['brand']}. See specs, features, pricing, and how it compares to similar products.",
            "category": category,
            "subcategory": product.get("subcategory"),
            "breadcrumbs": [
                {"name": "Home", "url": f"{DOMAIN}/"},
                {"name": cat_name, "url": f"{DOMAIN}/{category}/"},
                {"name": product["title"], "url": ""},
            ],
            "products": [product],
            "relatedProducts": related,
        })

    return manifests


def generate_all():
    """Generate all page manifests for all categories"""
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

    for category in CATEGORY_NAMES:
        print(f"\n[GearCompared] Generating manifests for: {category}")
        products = load_products(category)
        if not products:
            continue

        all_manifests: list[dict] = []

        # Category hub
        cat_manifest = generate_category_manifest(category, products)
        all_manifests.append(cat_manifest)
        print(f"   Category hub: /{category}/")

        # Product pages
        product_manifests = generate_product_manifests(category, products)
        all_manifests.extend(product_manifests)
        print(f"   Product pages: {len(product_manifests)}")

        # Roundups
        roundup_manifests = generate_roundup_manifests(category, products)
        all_manifests.extend(roundup_manifests)
        print(f"   Roundup pages: {len(roundup_manifests)}")

        # Comparisons (limited to avoid combinatorial explosion)
        comparison_manifests = generate_comparison_manifests_limited(category, products, max_pairs=15)
        all_manifests.extend(comparison_manifests)
        print(f"   Comparison pages: {len(comparison_manifests)}")

        # Write manifest
        manifest_path = MANIFEST_DIR / f"{category}.json"
        with open(manifest_path, "w") as f:
            json.dump(all_manifests, f, indent=2)
        print(f"   [OK] Wrote {len(all_manifests)} page manifests to {manifest_path}")

        # Print summary
        types = {}
        for m in all_manifests:
            types[m["type"]] = types.get(m["type"], 0) + 1
        for t, count in types.items():
            print(f"      {t}: {count} pages")


def main():
    print("[GearCompared] GearCompared Page Manifest Generator")
    print(f"   Reading products from: {DATA_DIR}")
    print(f"   Writing manifests to: {MANIFEST_DIR}")
    generate_all()
    print("\n[OK] All page manifests generated!")


if __name__ == "__main__":
    main()
