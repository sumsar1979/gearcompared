"""
Batch ASIN checker — uses DuckDuckGo external search to determine if an ASIN 
is indexed (i.e., real) or unindexed (likely dead / Dogs of Amazon).

HOW IT WORKS:
A dead ASIN like B08CK7TBP3 won't appear in DuckDuckGo search results at all.
A live ASIN will appear on amazon.com search results indexed by DuckDuckGo.

Run: python scripts/batch-check-asins-live.py
"""

import json
import urllib.request
import urllib.error
import time
import re

def check_asin_via_duckduckgo(asin, title_hint):
    """Check if ASIN appears in DuckDuckGo results — if indexed = likely live."""
    # DuckDuckGo lite search
    query = f"{asin} site:amazon.com"
    url = f"https://lite.duckduckgo.com/lite/?q={urllib.request.quote(query)}"
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"ERROR: {e}"
    
    # Check if the ASIN appears in the results (case-insensitive)
    if asin.lower() in html.lower():
        return "LIVE"
    
    # Check for "no results" indicators
    if "No results" in html or "no results" in html.lower():
        return "DEAD"
    
    # If ASIN not found but no explicit "no results", check product title hint
    if title_hint.lower()[:20] in html.lower():
        return "LIKELY_LIVE"
    
    return "UNKNOWN"

# Load products
products = []
for cat in ['standing-desks', 'kitchen-appliances']:
    with open(f'data/products/{cat}.json') as f:
        products.extend(json.load(f))

print(f"Checking {len(products)} ASINs via DuckDuckGo...")
print(f"{'ASIN':<12} {'STATUS':<15} {'Product':<50}")
print("-" * 80)

live = []
dead = []
unknown = []

for i, p in enumerate(products):
    asin = p['asin']
    title = p['title']
    status = check_asin_via_duckduckgo(asin, title)
    
    print(f"{asin:<12} {status:<15} {title[:48]}")
    
    if status == "LIVE" or status == "LIKELY_LIVE":
        live.append(p)
    elif status == "DEAD":
        dead.append(p)
    else:
        unknown.append(p)
    
    if i < len(products) - 1:
        time.sleep(1)  # Be polite

print(f"\n--- SUMMARY ---")
print(f"LIVE: {len(live)}")
print(f"DEAD: {len(dead)}")
print(f"UNKNOWN: {len(unknown)}")

if dead:
    print(f"\n🟡 DEAD ASINs:")
    for p in dead:
        print(f"  {p['asin']} — {p['title']}")

if unknown:
    print(f"\n⚪ UNKNOWN ASINs:")
    for p in unknown:
        print(f"  {p['asin']} — {p['title']}")
