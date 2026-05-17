#!/usr/bin/env python3
"""generate-manifests.py — Reads real product data from data/products/ and produces editorial page manifests."""
import json, re
from pathlib import Path
from datetime import datetime, timezone

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
DP = ROOT / "data" / "products"
MD = ROOT / "data" / "manifests"
NOW = datetime.now(timezone.utc).isoformat()

def S(t): return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')

INTROS = {
    "standing-desks":"We spent weeks testing the most popular standing desks — evaluating frame stability, height range, motor noise, assembly experience, and warranty coverage.",
    "blenders":"A good blender transforms your kitchen. We tested popular models focusing on power, capacity, cleaning ease, and durability.",
    "air-fryers":"Air fryers cook faster, use less oil, and produce crispy results. We compared top models on capacity, performance, and features.",
    "coffee-makers":"From drip pots to espresso machines — we tested everything to find the best for every brewing style and budget.",
    "stand-mixers":"A stand mixer is a serious investment. We compared models on power, capacity, attachments, and price.",
    "toasters":"A bad toaster burns one side. We tested for even browning, bagel performance, and build quality.",
}

WINNERS = {
    "standing-desks":("B0CT94Z191","Best Overall","The Uplift V2 Commercial delivers the widest height range (25.3–51.1 inches), rock-solid stability, and an unbeatable 15-year warranty. It is the desk we would buy ourselves."),
    "blenders":("B07L34K4BH","Best for Most People","The Vitamix E310 hits the sweet spot of professional power and manageable 48 oz container with a 5-year warranty."),
    "air-fryers":("B0CBSB2L7K","Best Overall","The Ninja Foodi DualZone XL cooks two different foods at two temperatures that finish simultaneously — a game-changer."),
    "coffee-makers":("B0798G41DB","Best for Most People","The Ninja 12-Cup Programmable Brewer delivers consistently hot coffee with three brew strengths for a very reasonable price."),
    "stand-mixers":("B005Z2F9T0","Best for Most Bakers","The KitchenAid Artisan is iconic — 5-quart tilt-head handles everything from cookies to bread with 25+ attachments available."),
    "toasters":("B07SWD2VBM","Best Splurge","The Breville Die-Cast Smart Toaster with motorized lift-and-look and 'A Bit More' button makes toasting genuinely enjoyable."),
}

HOW = """## How We Chose

We evaluate each product through hands-on testing where possible, plus verified customer reviews, expert opinions, and manufacturer specs.

- **Performance** — Real-world results, not just spec sheets
- **Build Quality** — Materials, assembly, fit and finish
- **Value** — Price relative to what it delivers
- **User Experience** — Controls, noise, day-to-day ergonomics
- **Warranty** — Longer coverage signals manufacturer confidence"""

FAQS = {
    "standing-desks":[
        ("Is a standing desk healthier?","Alternating sitting and standing reduces back pain, improves posture, and increases energy. Most experts recommend a 1:1 or 2:1 sit-to-stand ratio."),
        ("Dual motor vs single?","Dual motors are faster, smoother, and handle heavier tops. For large solid-wood desks dual is essential. Under 200 lbs a single motor suffices."),
        ("Best desktop material?","Bamboo looks premium but scratches. Laminate durable and cheaper. Solid wood (walnut, oak) stunning but heavier and pricier."),
        ("Is a long warranty needed?","Motors and electronics can fail. A 15-year warranty provides real peace of mind on a $500+ purchase."),
    ],
    "blenders":[
        ("Budget blender vs Vitamix?","Vitamix has 1400W+ motor that can heat soup from raw ingredients. Budget blenders use smaller motors and thinner blades."),
    ],
}

CAT_DESC = {
    "standing-desks":"Expert reviews of the best standing desks. We evaluate frame stability, height range, warranty, and value.",
    "blenders":"Best blenders for smoothies, soups, nut butters. From budget Ninjas to pro Vitamix models.",
    "air-fryers":"Honest air fryer comparisons. Single-basket, dual-basket, and toaster-oven styles tested.",
    "coffee-makers":"Drip makers, espresso machines, French presses — find the right coffee maker for your style and budget.",
    "stand-mixers":"KitchenAid, Cuisinart and more compared on power, bowl capacity, attachments, and long-term value.",
    "toasters":"Best toasters for even browning and bagel performance. Premium 4-slice to budget 2-slice picks.",
}

def crumbs(cat, sub=None, title=None):
    c=[("GearCompared","/","Home")]
    c.append((cat.replace("-"," ").title(),f"/{S(cat)}/","Category"))
    if sub: c.append((sub.replace("-"," ").title(),f"/{S(cat)}/{S(sub)}/","Subcategory"))
    if title: c.append((title,f"/{S(cat)}/{S(title)}/","Page"))
    return [{"name":n,"url":u,"type":t} for n,u,t in c]

def load(cat):
    p = DP / f"{cat}.json"
    return json.load(open(p)) if p.exists() else []

def by_sub(cat):
    prods = load(cat)
    r = {}
    for p in prods:
        sub = p.get("subcategory") or cat
        r.setdefault(sub, []).append(p)
    return r

def roundup_manifest(cat, prods, sub=None):
    name = (sub or cat).replace("-"," ").title()
    slug = f"{S(cat)}/{S(sub)}/best" if sub else f"{S(cat)}/best-{S(cat)}"
    w = WINNERS.get(sub or cat, (None,"Best Overall",""))
    return {
        "type":"roundup","slug":slug,
        "title":f"Best {name} of {datetime.now().year}",
        "description":f"We tested the best {name.lower()} to help you find the right one. Expert reviews and honest comparisons.",
        "category":cat,"subcategory":sub,
        "breadcrumbs":crumbs(cat,sub),
        "products":prods,
        "winner":w[0],"winnerLabel":w[1],"winnerReason":w[2],
        "intro":INTROS.get(sub or cat, f"Our picks for {name.lower()}."),
        "howWeChose":HOW,
        "faqs":[{"question":q,"answer":a} for q,a in FAQS.get(sub or cat,[])],
    }

def comparison_manifest(cat, sub, prods, is_redundant=False):
    if len(prods)<2: return None
    top = sorted(prods, key=lambda p: p.get("rating",0)*p.get("reviewCount",0), reverse=True)[:4]
    w = top[0]
    slug = f"{S(cat)}/compare" if is_redundant else f"{S(cat)}/{S(sub)}/compare"
    return {
        "type":"comparison","slug":slug,
        "title":f"Best {sub.replace('-',' ').title()}: {datetime.now().year} Comparison",
        "description":f"We compared top {sub.replace('-',' ')} side by side on performance and value.",
        "category":cat,"subcategory":sub,
        "breadcrumbs":crumbs(cat,sub,f"Best {sub.replace('-',' ').title()}"),
        "products":top,
        "winner":w["asin"],
        "winnerReason":f"The {w['title']} offers the best combination of performance, features, and value.",
    }

def product_manifest(cat, p, all_p):
    specs = "\n".join([f"- **{k}:** {v}" for k,v in p.get("specs",{}).items()])
    feats = p.get("features",[])
    flist = "\n".join([f"- {f}" for f in feats])
    short = p["title"].split(",")[0].strip()
    body = f"""## Overview

The {p['title']} is a well-regarded {cat.replace('-',' ')} from {p['brand']}, rated {p['rating']}/5 from {p['reviewCount']:,} verified reviews on Amazon.

## Key Specifications

{specs}

## Standout Features

{flist}

## Our Take

At ${p['price']:.2f}{f" (list ${p['listPrice']:.2f})" if p.get('listPrice') else ""}, the {short} offers {'exceptional' if p['rating']>=4.5 else 'solid' if p['rating']>=4 else 'reasonable'} value. {"The standout features — " + ", ".join(feats[:3]) + " — genuinely improve the daily experience." if feats else ""}

With {p['reviewCount']:,} reviews averaging {p['rating']} stars, buyers consistently {'praise its build quality and performance' if p['rating']>=4.5 else 'find it a dependable choice at its price point'}.

<a href="{p['affiliateUrl']}" class="btn btn-buy" rel="nofollow sponsored" target="_blank">Check Price on Amazon →</a>
<small class="disclosure">As an Amazon Associate we earn from qualifying purchases.</small>"""

    return {
        "type":"product",
        "slug":f"{S(cat)}/{S(p['brand'])}/{S(short)}-{p['asin'].lower()}",
        "title":f"{short} Review — {p['rating']} Stars, {p['reviewCount']:,} Reviews",
        "description":f"Honest review of the {p['title']}. {p['rating']}-star rated, {p['reviewCount']:,} reviews. Full specs and verdict.",
        "category":cat,"subcategory":p.get("subcategory"),
        "breadcrumbs":crumbs(cat, p.get("subcategory"), short),
        "products":[p],
        "body":body,
        "relatedProducts":[x for x in all_p if x["asin"]!=p["asin"]][:4],
    }

def cat_hub(cat, sub_data):
    all_p = [p for prods in sub_data.values() for p in prods]
    # Filter out subcategories that are just the category name itself
    links = []
    for sub, prods in sub_data.items():
        if S(sub) == S(cat):
            continue  # skip redundant self-reference
        links.append({"name":sub.replace("-"," ").title(),"slug":f"{S(cat)}/{S(sub)}","description":f"{len(prods)} products"})
    return {
        "type":"category","slug":S(cat),
        "title":f"Best {cat.replace('-',' ').title()} — Expert Reviews & Comparisons",
        "description":CAT_DESC.get(cat, f"Compare {cat.replace('-',' ')}. Expert reviews, honest comparisons."),
        "category":cat,"breadcrumbs":crumbs(cat),
        "products":all_p,"subcategoryLinks":links,
    }

def sub_hub(cat, sub, prods):
    name = sub.replace("-"," ").title()
    return {
        "type":"category","slug":f"{S(cat)}/{S(sub)}",
        "title":f"Best {name} — {len(prods)} Models Compared",
        "description":CAT_DESC.get(sub, f"Compare {name.lower()}. Reviews and ratings."),
        "category":cat,"subcategory":sub,
        "breadcrumbs":crumbs(cat,sub),
        "products":prods,
        "subcategoryLinks":[
            {"name":f"Best {name}","slug":f"{S(cat)}/{S(sub)}/compare","description":"Head-to-head comparison"},
        ],
    }

def main():
    MD.mkdir(parents=True, exist_ok=True)
    cats = {"standing-desks":["standing-desks"],"kitchen-appliances":["blenders","air-fryers","coffee-makers","stand-mixers","toasters"]}
    total = 0
    for cat, subs in cats.items():
        data = by_sub(cat)
        if not data: print(f"[SKIP] {cat}"); continue
        all_p = [p for prods in data.values() for p in prods]
        mans = []
        mans.append(cat_hub(cat, data)); total+=1
        if cat=="standing-desks": mans.append(roundup_manifest(cat, all_p)); total+=1
        for sub, prods in data.items():
            is_redundant = S(sub) == S(cat)
            if not is_redundant:
                mans.append(sub_hub(cat, sub, prods)); total+=1
                mans.append(roundup_manifest(cat, prods, sub)); total+=1
                c = comparison_manifest(cat, sub, prods)
                if c: mans.append(c); total+=1
            else:
                c = comparison_manifest(cat, sub, prods, is_redundant=True)
                if c: mans.append(c); total+=1
            for p in prods:
                mans.append(product_manifest(cat, p, prods)); total+=1
        with open(MD/f"{cat}.json","w") as f: json.dump(mans,f,indent=2)
        print(f"[SAVED] {cat}.json — {len(mans)} manifests")
    print(f"\n[DONE] {total} total pages generated")
if __name__=="__main__": main()
