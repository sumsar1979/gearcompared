#!/usr/bin/env python3
"""
health-check.py — Validate the GearCompared data pipeline and site integrity.
Checks: JSON validity, image URLs, page counts, manifest integrity.
"""

import json
import sys
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "products"
MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"


def check_json_valid(filepath: Path) -> tuple[bool, str]:
    """Verify a JSON file is valid"""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return True, f"{len(data)} entries"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, str(e)


def check_image_url(url: str) -> tuple[bool, str]:
    """Check if an image URL is reachable (HEAD request)"""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200, f"HTTP {resp.status}"
    except Exception as e:
        return False, str(e)


def check_product_schema(product: dict) -> list[str]:
    """Validate product conforms to expected schema"""
    issues = []
    required = ["asin", "title", "brand", "category", "price", "rating",
                "reviewCount", "imageUrl", "specs", "features", "affiliateUrl"]
    for field in required:
        if field not in product:
            issues.append(f"Missing required field: {field}")
    if "price" in product and (not isinstance(product["price"], (int, float)) or product["price"] <= 0):
        issues.append("Invalid price")
    if "rating" in product and (not isinstance(product["rating"], (int, float)) or product["rating"] < 1 or product["rating"] > 5):
        issues.append("Rating out of range")
    if "reviewCount" in product and (not isinstance(product["reviewCount"], int) or product["reviewCount"] < 0):
        issues.append("Invalid reviewCount")
    return issues


def main():
    print("[GearCompared] GearCompared Health Check")
    print(f"   Run at: {datetime.now(timezone.utc).isoformat()}")
    print()

    all_ok = True
    total_products = 0
    total_pages = 0

    # --- Check product data ----------------------------------
    print("[PROD] Product Data:")
    for json_file in sorted(DATA_DIR.glob("*.json")):
        ok, msg = check_json_valid(json_file)
        status = "[OK]" if ok else "[FAIL]"
        print(f"   {status} {json_file.name}: {msg}")
        if not ok:
            all_ok = False
            continue

        # Validate products
        with open(json_file, "r") as f:
            products = json.load(f)
        total_products += len(products)
        product_issues = 0
        for p in products:
            issues = check_product_schema(p)
            if issues:
                product_issues += 1
                print(f"      [WARN]  {p.get('asin', 'UNKNOWN')}: {', '.join(issues)}")
        if product_issues > 0:
            print(f"      [WARN]  {product_issues} products with schema issues")
            all_ok = False

    print(f"   Total products: {total_products}")
    print()

    # --- Check page manifests --------------------------------
    print("[PAGES] Page Manifests:")
    for json_file in sorted(MANIFEST_DIR.glob("*.json")):
        ok, msg = check_json_valid(json_file)
        status = "[OK]" if ok else "[FAIL]"
        print(f"   {status} {json_file.name}: {msg}")
        if not ok:
            all_ok = False
            continue

        with open(json_file, "r") as f:
            manifests = json.load(f)
        total_pages += len(manifests)

        # Check for required fields in manifests
        for m in manifests:
            required = ["type", "slug", "title", "products", "category", "breadcrumbs"]
            for field in required:
                if field not in m:
                    print(f"      [WARN]  Manifest {m.get('slug', '?')}: missing '{field}'")
                    all_ok = False

    print(f"   Total pages: {total_pages}")
    print()

    # --- Check image URLs (sample) ---------------------------
    print("[IMG]  Image URLs (sampling 5):")
    checked = 0
    for json_file in sorted(DATA_DIR.glob("*.json")):
        if checked >= 5:
            break
        with open(json_file, "r") as f:
            products = json.load(f)
        for p in products[:2]:
            if checked >= 5:
                break
            url = p.get("imageUrl", "")
            if url:
                ok, msg = check_image_url(url)
                status = "[OK]" if ok else "[WARN]"
                print(f"   {status} {url}: {msg}")
                checked += 1
    print()

    # --- Summary ---------------------------------------------
    print("-" * 50)
    if all_ok:
        print("[OK] All checks passed!")
    else:
        print("[FAIL] Some checks failed — review issues above")

    print(f"   Products: {total_products}")
    print(f"   Pages to generate: {total_pages}")
    print(f"   Categories: {len(list(DATA_DIR.glob('*.json')))}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
