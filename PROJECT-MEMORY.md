# GearCompared — Full Project Context

> Last updated: 2026-05-18. 63 pages live. Phases 1–3 complete.

---

## Quick Reference

- **Root**: `C:\Users\Eland\.openclaw\workspace\gearcompared`
- **GitHub**: `https://github.com/sumsar1979/gearcompared`
- **Live**: gearcompared.com (Cloudflare Pages, auto-deploy on push)
- **Affiliate tag**: `gearcompared2-20`
- **All links**: Amazon search URLs (`/s?k=...`) — ZERO `/dp/` links
- **Byline**: "GearCompared Editorial Team" — no fictional personas
- **Tech**: Astro static, 63 pages, `@astrojs/sitemap`

---

## What's Complete

### Phase 1 — Technical SEO
- Sitemap with priority rules, `/go/` filtered
- `robots.txt`, `llms.txt`, custom 404 page
- Canonical URLs everywhere
- JSON-LD: Product, Comparison, ItemList, FAQ, BreadcrumbList (all wired per layout)

### Phase 2 — Content Pages
- `/about/`, `/contact/`, `/methodology/`
- 3 buying guides: standing desks, blenders, air fryers
- 3 head-to-head comparisons: Uplift V2 vs FlexiSpot, Vitamix vs Ninja, KitchenAid vs Cuisinart

### Phase 3 — Layout Improvements
- Pros/cons cards + "Who it's for / Not for" on all 30 products
- 196 internal links via `relatedGuides`
- Sticky TOC (desktop, ≤900px hidden) on comparison/roundup pages
- Winner boxes: badge, price, rating, CTA, disclosure

### Automation
- `scripts/link-checker.py` — zero `/dp/` check. Cron job `0b51566a`, every 6h, 180s timeout.

---

## Still To Do

1. **4 blog posts**: desk ergonomics, sit-stand ratio, blender tips, air fryer vs oven
2. **2 targeted pages**: standing desks under $300, standing desks for small spaces
3. **GSC + GA4** — user must set up. Needs GA4 Measurement ID (`G-XXXXXXXXXX`).

---

## Key Files

| File | Purpose |
|------|---------|
| `CONTENT-PLAN.md` | Keyword research, competitor landscape, content priorities |
| `BASELINE-AUDIT.md` | Site audit before SEO work |
| `src/lib/structured-data.ts` | JSON-LD generation functions |
| `src/components/StickyTOC.astro` | Sticky table of contents component |
| `src/pages/[...slug].astro` | Dynamic slug router — passes `relatedGuides` to all layouts |
| `scripts/link-checker.py` | Verifies zero `/dp/` links, regenerates manifests |
| `scripts/add-pros-cons.py` | Generated pros/cons/whoFor data for all 30 products |
| `scripts/add-related-pages.py` | Computed `relatedGuides` by category overlap |

### Layouts (all modified in this session)
- `BaseLayout.astro` — canonicals, schema slot, twitter cards, OG, footer
- `ProductLayout.astro` — pros/cons, who-for, product schema, breadcrumbs
- `ComparisonLayout.astro` — TOC, winner box, comparison schema
- `RoundupLayout.astro` — TOC, winner box, FAQ schema
- `CategoryLayout.astro` — breadcrumbs, relatedGuides
