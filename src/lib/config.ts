// Site configuration for GearCompared
export interface CategoryConfig {
  slug: string;
  name: string;
  description: string;
  subcategories: string[];
}

export interface SiteConfig {
  siteName: string;
  domain: string;
  tagline: string;
  defaultAmazonTag: string;
  categories: CategoryConfig[];
  social: {
    twitter: string;
    facebook: string;
    instagram: string;
    youtube: string;
  };
}

const config: SiteConfig = {
  siteName: 'GearCompared',
  domain: 'gearcompared.com',
  tagline: 'Honest product comparisons to help you choose the best gear',
  defaultAmazonTag: 'gearcompared2-20',
  categories: [
    {
      slug: 'standing-desks',
      name: 'Standing Desks',
      description: 'Compare the best standing desks for your home office',
      subcategories: ['electric', 'manual', 'converter', 'gaming'],
    },
    {
      slug: 'kitchen-appliances',
      name: 'Kitchen Appliances',
      description: 'Find the best kitchen appliances for your cooking needs',
      subcategories: ['blenders', 'air-fryers', 'coffee-makers', 'stand-mixers', 'toasters'],
    },
  ],
  social: {
    twitter: '',
    facebook: '',
    instagram: '',
    youtube: '',
  },
};

export type { SiteConfig as default };
export { config };
export default config;
