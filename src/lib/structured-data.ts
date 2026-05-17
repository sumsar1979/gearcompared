// Structured Data Library — schema.org JSON-LD generators

// ─── Shared Types ────────────────────────────────────────────

export interface ProductData {
  asin: string;
  title: string;
  brand: string;
  category: string;
  price: number;
  listPrice?: number;
  rating: number;
  reviewCount: number;
  imageUrl: string;
  specs: Record<string, string>;
  features: string[];
  affiliateUrl: string;
}

export interface Breadcrumb {
  name: string;
  url: string;
}

// ─── Product ─────────────────────────────────────────────────

export function generateProductLD(product: ProductData): Record<string, unknown> {
  const offer: Record<string, unknown> = {
    '@type': 'Offer',
    price: product.price,
    priceCurrency: 'USD',
    availability: 'https://schema.org/InStock',
    url: product.affiliateUrl,
  };
  if (product.listPrice && product.listPrice > product.price) {
    offer.priceSpecification = {
      '@type': 'UnitPriceSpecification',
      price: product.listPrice,
      priceCurrency: 'USD',
    };
  }

  return {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.title,
    description: `${product.title} by ${product.brand}. ${product.features.slice(0, 3).join('. ')}`,
    sku: product.asin,
    brand: { '@type': 'Brand', name: product.brand },
    image: product.imageUrl,
    offers: offer,
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: product.rating,
      reviewCount: product.reviewCount,
    },
    category: product.category,
  };
}

// ─── ComparisonTable ─────────────────────────────────────────

export function generateComparisonLD(
  products: ProductData[],
  pageTitle: string,
  pageUrl: string,
): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: pageTitle,
    url: pageUrl,
    mainEntity: {
      '@type': 'ItemList',
      name: pageTitle,
      numberOfItems: products.length,
      itemListElement: products.map((p, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        item: generateProductLD(p),
      })),
    },
  };
}

// ─── ItemList (Roundup) ──────────────────────────────────────

export function generateItemListLD(
  products: ProductData[],
  listTitle: string,
  listUrl: string,
): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: listTitle,
    url: listUrl,
    numberOfItems: products.length,
    itemListElement: products.map((p, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      item: generateProductLD(p),
    })),
  };
}

// ─── BreadcrumbList ──────────────────────────────────────────

export function generateBreadcrumbLD(breadcrumbs: Breadcrumb[]): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((b, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: b.name,
      item: b.url,
    })),
  };
}

// ─── FAQ ─────────────────────────────────────────────────────

export interface FAQItem {
  question: string;
  answer: string;
}

export function generateFAQLD(faqs: FAQItem[]): Record<string, unknown> {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  };
}

// ─── Merge multiple LD objects ───────────────────────────────

export function mergeLD(...objects: Record<string, unknown>[]): Record<string, unknown>[] {
  return objects;
}
