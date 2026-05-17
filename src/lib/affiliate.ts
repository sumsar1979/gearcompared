// Affiliate Link Manager — ASIN to affiliate URL conversion and click tracking

import { config } from './config';

const AMAZON_BASE = 'https://www.amazon.com/dp';

/**
 * Convert an ASIN to a tagged affiliate URL.
 */
export function asinToAffiliateUrl(asin: string, tag?: string): string {
  const t = tag || config.defaultAmazonTag;
  return `${AMAZON_BASE}/${asin}?tag=${t}&linkCode=ogi&th=1&psc=1`;
}

/**
 * Generate the /go/[asin] redirect path for internal click tracking.
 */
export function goPath(asin: string): string {
  return `/go/${asin}`;
}

/**
 * Click event record — stored locally, no external dependency.
 */
export interface ClickEvent {
  asin: string;
  page: string;
  timestamp: string;
}

const clickEvents: ClickEvent[] = [];

/**
 * Track a click event. In production this would be persisted;
 * for now it's an in-memory array.
 */
export function trackClick(asin: string, page: string): void {
  clickEvents.push({
    asin,
    page,
    timestamp: new Date().toISOString(),
  });
}

/**
 * Retrieve recent click events (for analytics display).
 */
export function getClickEvents(limit?: number): ClickEvent[] {
  const sorted = [...clickEvents].reverse();
  return limit ? sorted.slice(0, limit) : sorted;
}
