# GearCompared Baseline Audit — 2026-05-18

## Performance (live site, measured via browser)
| Page | FCP | Title OK | Meta Description | H1 | Schema | Images |
|------|-----|----------|-----------------|----|--------|--------|
| / (home/roundup) | 96ms | ✅ | ✅ 155 chars | ✅ | ❌ | 5, all alt |
| /standing-desks/vari/... (product) | 144ms | ✅ | ✅ 155 chars | ✅ | ❌ | 1, alt OK |
| /kitchen-appliances/blenders/compare/ | 132ms | ✅ | ✅ | ✅ | ❌ | — |
| /kitchen-appliances/ (category) | fast | ✅ | — | ✅ | ❌ | — |
| /disclosure/ | fast | ✅ | — | ✅ | ❌ | — |

**Lighthouse estimate**: Performance 95+ (static HTML, no JS bundle, 96ms FCP), SEO ~70 (missing sitemap, robots, schema), Best Practices ~85, Accessibility ~90.

## Missing Technical SEO
- [ ] robots.txt (not generated)
- [ ] sitemap.xml (not generated)
- [ ] /llms.txt
- [ ] 404 page
- [ ] JSON-LD schema on every page (library exists but NOT wired into templates)
- [ ] Canonical tags (BaseLayout has no `<link rel="canonical">`)
- [ ] Twitter card meta tags
- [ ] OG image tags
- [ ] Dynamic title suffix handling (BaseLayout always appends `| GearCompared`)

## Missing Pages
- [ ] /methodology/ — "How We Test" — critical for E-E-A-T
- [ ] /about/ — author/team page
- [ ] /contact/ — trust signal + GSC verification path
- [ ] /blog/ — informational content hub
- [ ] Author profile pages

## Missing Page Features (Templates)
- [ ] Sticky table of contents (desktop)
- [ ] Winner box above fold on comparisons (verdict exists but not prominent)
- [ ] "Last updated" dates rendered consistently
- [ ] Author byline with link to author page
- [ ] FTC disclosure above fold per spec (currently small text under CTA)
- [ ] "What we like / don't like" structured pros/cons sections
- [ ] "Who it's for / not for" sections
- [ ] Price tracking or "price range" note
- [ ] Jump links in long-form content

## Content Status
- 30 product reviews ✅ (genuine editorial content)
- 5 category hubs ✅
- 6 roundup pages ✅
- 5 comparison pages ✅
- 3 static pages (disclosure, privacy, terms) ✅
- 0 blog/informational posts ❌
- 0 pillar buyer's guides ❌
- 0 "X vs Y" dedicated comparison pages ❌ (current comparison pages are group comparisons)

## Internal Linking (spot check)
- Homepage links to: standing-desks category only
- Product pages: related products (4), breadcrumbs, navigation
- No cross-category linking
- No "further reading" or "related guides" sections

## GSC / GA4
- Not connected, not verified

## Known Issues
- `lib/affiliate.ts` generates `/dp/` URLs (stale — site now uses search URLs in product JSONs)
- No build-time sitemap generation (needs @astrojs/sitemap)
- Manifest generation creates fresh data each build including `lastUpdated` — good for freshness
