import type { Config } from 'drizzle-kit';

export default {
  schema: './lib/db/schema.ts',
  out: './drizzle',
  dbCredentials: {
    connectionString: (process.env.DATABASE_URL_DIRECT || process.env.DATABASE_URL)!,
  },
} satisfies Config;
