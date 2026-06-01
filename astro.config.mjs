// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

import cloudflare from '@astrojs/cloudflare';

// https://astro.build/config
export default defineConfig({
  site: 'https://gearcompared.com',
  output: 'static',

  build: {
    format: 'directory',
  },

  trailingSlash: 'always',

  integrations: [
    sitemap({
      filter: (page) => !page.includes('/go/') && !page.includes('/api/'),
      changefreq: 'weekly',
      priority: 1.0,
      serialize: (item) => {
        // Category hubs and roundups: higher priority
        if (/^\/(standing-desks|kitchen-appliances)(\/|$)/.test(item.url) && item.url.split('/').length <= 4) {
          return { ...item, priority: 0.9 };
        }
        // Product pages: 0.7
        if (item.url.includes('/reviews/') || /-[a-z0-9]{10}\/$/.test(item.url)) {
          return { ...item, priority: 0.7 };
        }
        return item;
      },
    }),
  ],

  adapter: cloudflare(),
});