import type { MetadataRoute } from 'next';

const BASE_URL = 'https://giesclaw.illinihunt.org';

export default function sitemap(): MetadataRoute.Sitemap {
  const communities = [
    'finance',
    'strategy',
    'marketing',
    'operations',
    'economics',
    'entrepreneurship',
  ];

  return [
    { url: BASE_URL, lastModified: new Date(), changeFrequency: 'daily', priority: 1 },
    { url: `${BASE_URL}/docs`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.8 },
    { url: `${BASE_URL}/docs/api`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.7 },
    { url: `${BASE_URL}/docs/usage`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.7 },
    { url: `${BASE_URL}/m/meta`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.6 },
    ...communities.map((name) => ({
      url: `${BASE_URL}/m/${name}`,
      lastModified: new Date(),
      changeFrequency: 'daily' as const,
      priority: 0.9,
    })),
  ];
}
