# GearCompared

## 🏗️ What Is This?

A **programmatic SEO affiliate site** for `gearcompared.com` that compares standing desks and kitchen appliances using product data.

The site generates hundreds of SEO-optimized static pages — product comparisons ("X vs Y"), roundups ("Best 10 X"), individual product pages, and category hubs — all with structured data, mobile-first CSS, and affiliate links.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Generate mock product data
npm run fetch:mock

# Generate page manifests
npm run generate

# Start dev server
npm run dev

# Build for production
npm run build

# Run health checks
npm run health
```

## 📁 Project Structure

```
src/
├── layouts/           # Astro layout templates
│   ├── ComparisonLayout.astro
│   ├── RoundupLayout.astro
│   ├── ProductLayout.astro
│   └── CategoryLayout.astro
├── lib/               # TypeScript utility modules
│   ├── config.ts      # Site configuration
│   ├── structured-data.ts  # JSON-LD generators
│   └── affiliate.ts   # Affiliate link management
├── pages/
│   └── [...slug].astro  # Catch-all routing
└── styles/
    └── global.css     # Site-wide CSS (custom properties)

scripts/
├── fetch-products.py  # Product data pipeline
├── generate-pages.py  # Page manifest generator
├── health-check.py    # Data/site integrity checker
└── config.json        # Product ASIN config

data/
├── products/          # Product JSON by category
└── manifests/         # Page manifests for Astro

.github/workflows/
├── deploy.yml         # Cloudflare Pages deploy
└── weekly-refresh.yml # Weekly product data refresh
```

## 🛠️ Architecture

### Data Pipeline
1. `fetch-products.py` → reads ASIN config (or generates mock data) → writes `data/products/[category].json`
2. `generate-pages.py` → reads product JSON → generates page manifests → writes `data/manifests/[category].json`
3. Astro's `[...slug].astro` → reads manifests → renders appropriate layout

### Page Types
- **Comparison** (`ComparisonLayout`): "X vs Y" pages with comparison table, winner callout, detailed breakdowns
- **Roundup** (`RoundupLayout`): "Best 10 X" ranked lists with pros/cons, FAQ section
- **Product** (`ProductLayout`): Individual product pages with specs, features, related products
- **Category** (`CategoryLayout`): Category hubs with subcategory links, top products grid, popular comparisons

### Structured Data
Every page includes schema.org JSON-LD: Product, ComparisonTable, ItemList, BreadcrumbList, FAQ

### Affiliate Links
All Amazon links use the `/go/[asin]` pattern with proper `rel="nofollow sponsored"` attributes.

## 🔧 Configuration

Edit `src/lib/config.ts` to change:
- Site name, domain, tagline
- Amazon affiliate tag
- Categories
- Social handles

## 📊 Status

- [x] Astro static site foundation
- [x] 4 layout templates with typed props
- [x] Structured data library (Product, ComparisonTable, ItemList, BreadcrumbList, FAQ)
- [x] Affiliate link manager
- [x] Mock product data pipeline (10 products per category)
- [x] Page manifest generator
- [x] Health check script
- [x] Mobile-first CSS with custom properties
- [x] GitHub Actions workflows (deploy + weekly refresh)
- [ ] Amazon PAAPI integration (replace mock data)
- [ ] Real product images (currently using picsum.photos placeholders)
