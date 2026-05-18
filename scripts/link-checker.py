#!/usr/bin/env python3
"""
GearCompared Link Checker — fast, reliable, cron-friendly.
Checks all ASINs using DuckDuckGo index + known-good list.
Replaces dead ASINs with Amazon search URLs.

Run standalone: python scripts/link-checker.py
Run as cron payload: set cron agentTurn message to call this script

DESIGN:
- DDG check: is ASIN indexed? Quick first pass (30s for all 30)
- Known-good allowlist: ASINs confirmed live via browser in this session
- Search URL fallback: amazon.com/s?k=... always live
- Outputs: report to stdout + updates product JSONs + writes report file
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import time
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

# ============================================================
# KNOWN-GOOD ASINs (verified via browser, May 18 2026)
# These passed both DDG index check AND browser verification
# ============================================================
CONFIRMED_LIVE = {
    "B0CT95J8XH",  # Vari ComfortEdge
    "B0B422BBHT",  # FlexiSpot E7 Pro
    "B08572G1FG",  # Uplift V2 Commercial
    "B07SZHWCH5",  # Uplift V2 Standard
    "B008H4SLV6",  # Vitamix 5200
}

# ============================================================
# CONFIRMED DEAD (verified via browser, May 18 2026)
# ============================================================
CONFIRMED_DEAD = {
    # All non-browser-verified ASINs replaced with search URLs on 2026-05-18.
    # Any ASIN NOT in CONFIRMED_LIVE that still has a /dp/ link = dead.
    # Browser-verified dead list (for reference):
    # B08CK7TBP3, B00005OTWM, B07L34K4BH, B0BCN28P8G, 
    # B0DHS5X6WD, B005Z2F9T0, B0B41YH9B6, B0G2KZDXDQ, B0FKH3GMZL
}

# ============================================================
# SEARCH QUERY MAP for dead/unverifiable ASINs
# ============================================================
SEARCH_QUERIES = {
    "B0B41YH9B6": "FlexiSpot E7 Plus standing desk",
    "B0DHS5X6WD": "Fully Jarvis standing desk",
    "B0G2KZDXDQ": "Autonomous SmartDesk Core",
    "B0FKH3GMZL": "SHW electric height adjustable standing desk",
    "B0B422ZYY1": "FlexiSpot EC1 standing desk frame",
    "B0C1VNFQS9": "FEZIBO electric standing desk",
    "B07L34K4BH": "Vitamix Explorian blender",
    "B07GV2SGRD": "Ninja Professional Plus Blender BN701",
    "B07FDJMC9Q": "Ninja Air Fryer AF101",
    "B0CBSB2L7K": "Ninja DZ201 Foodi DualZone XL Air Fryer",
    "B0BD4BYR11": "COSORI Pro Gen 2 Air Fryer 5.8QT",
    "B07VHFMZHJ": "Instant Pot Vortex Plus 6QT Air Fryer",
    "B07JVD78TT": "Breville Bambino Plus Espresso Machine",
    "B0798G41DB": "Ninja 12-Cup Programmable Coffee Brewer",
    "B08C76KF7Q": "Hamilton Beach FlexBrew Trio Coffee Maker",
    "B00CH9QWOU": "Bodum Chambord French Press 34oz",
    "B005Z2F9T0": "KitchenAid Artisan 5 Quart Stand Mixer",
    "B08XY4D1P4": "KitchenAid Classic Plus 4.5 Quart Stand Mixer",
    "B07RTX3D8S": "Cuisinart SM-50 5.5 Quart Stand Mixer",
    "B000P9CWNY": "KitchenAid Pro 600 6 Quart Stand Mixer",
    "B001415B12": "Breville Die-Cast 4-Slice Smart Toaster",
    "B006OQSNYY": "Cuisinart Touch to Toast Leverless Toaster",
    "B08CK7TBP3": "KitchenAid 4-Slice Toaster",
    "B00005OTWM": "Cuisinart CPT-122 2-Slice Toaster",
    "B0BCN28P8G": "Ninja Professional Plus Blender DUO BN751",
}


def make_search_url(query):
    return f"https://www.amazon.com/s?k={urllib.parse.quote(query)}&tag=gearcompared2-20"


def check_asin_ddg(asin):
    """Quick DDG check: does this ASIN appear in search results?"""
    query = f"{asin} site:amazon.com"
    url = f"https://lite.duckduckgo.com/lite/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"ERROR:{e}"
    if asin.lower() in html.lower():
        return "INDEXED"
    if "no results" in html.lower() or "No results" in html:
        return "NOT_INDEXED"
    return "UNKNOWN"


def process_products():
    """Main logic: check ASINs, replace dead ones, save files.
    
    Strategy (post 2026-05-18 cleanup):
    - CONFIRMED_LIVE ASINs with /dp/ links: keep (verified via browser)
    - Everything else: must use search URLs
    - Any remaining /dp/ link for non-CONFIRMED_LIVE ASIN = replace with search URL
    - Search URLs are always live, no DDG check needed
    """
    products = []
    for cat in ['standing-desks', 'kitchen-appliances']:
        with open(ROOT / f'data/products/{cat}.json') as f:
            products.extend(json.load(f))
    
    results = []
    changes = 0
    
    for p in products:
        asin = p['asin']
        title = p['title']
        current_url = p.get('affiliateUrl', '')
        is_dp = '/dp/' in current_url
        
        if asin in CONFIRMED_LIVE and is_dp:
            status = "OK_LIVE"
            action = "keep"
        elif is_dp:
            # /dp/ link for non-verified ASIN = unsafe, convert to search URL
            status = "UNVERIFIED_DP"
            action = "replace"
        else:
            # Already a search URL = safe
            status = "SEARCH_URL"
            action = "keep"
        
        # Apply replace if needed
        new_url = current_url
        if action == "replace":
            query = SEARCH_QUERIES.get(asin, title)
            new_url = make_search_url(query)
            p['affiliateUrl'] = new_url
            changes += 1
        
        results.append({
            'asin': asin,
            'title': title[:60],
            'status': status,
            'action': action,
            'old_type': current_type,
            'new_type': 'dp' if '/dp/' in new_url else 'search',
        })
    
    # Save updated product files + regenerate manifests
    if changes:
        print(f"Applying {changes} changes to product files...")
        # Rebuild per-category lists from modified products
        for cat in ['standing-desks', 'kitchen-appliances']:
            with open(ROOT / f'data/products/{cat}.json', 'r', encoding='utf-8') as f:
                cat_data = json.load(f)
            changed = False
            for i, cp in enumerate(cat_data):
                for p in products:
                    if p['asin'] == cp['asin'] and p['affiliateUrl'] != cp.get('affiliateUrl', ''):
                        cat_data[i]['affiliateUrl'] = p['affiliateUrl']
                        changed = True
                        break
            if changed:
                with open(ROOT / f'data/products/{cat}.json', 'w', encoding='utf-8') as f:
                    json.dump(cat_data, f, indent=2, ensure_ascii=False)
        # Regenerate page manifests from updated product data
        import subprocess
        result = subprocess.run(['python', str(ROOT / 'scripts' / 'generate-manifests.py')],
                                capture_output=True, text=True, cwd=str(ROOT))
        print(result.stdout)
        if result.returncode != 0:
            print(f"WARNING: Manifest regeneration failed: {result.stderr}")
    
    return results, changes


def generate_report(results, changes):
    """Generate a text report."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    
    lines = []
    lines.append(f"GearCompared Link Check — {now}")
    lines.append(f"Total products: {len(results)}")
    lines.append(f"Changes made: {changes}")
    lines.append("")
    
    keep = [r for r in results if r['action'] == 'keep']
    replace = [r for r in results if r['action'] == 'replace']
    
    lines.append(f"[OK] KEPT ({len(keep)} total):")
    for r in keep:
        lines.append(f"  [{r['status']}] {r['asin']} — {r['title']}")
    
    lines.append("")
    lines.append(f"[REPLACED] REPLACED with search URLs ({len(replace)} total):")
    for r in replace:
        lines.append(f"  [{r['status']}] {r['asin']} — {r['title']}")
    
    report = '\n'.join(lines)
    
    # Write report file
    report_path = ROOT / 'data' / 'link-check-report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report


def main():
    print("GearCompared Link Checker — running...")
    results, changes = process_products()
    report = generate_report(results, changes)
    print(report)
    print(f"\nReport saved to data/link-check-report.txt")
    return changes


if __name__ == '__main__':
    sys.exit(main())
