/**
 * Create the missing `notifications` table if absent.
 *
 * Why: comment creation currently 500s after inserting the comment because
 * it tries to insert notifications, but the table doesn't exist in this DB.
 *
 * NOTE: Prefer using `npm run db:push` instead, which syncs the entire schema.
 * This script exists only as a quick fix for existing databases.
 *
 * Usage:
 *   export $(grep -v '^#' .env.local | xargs)
 *   npx tsx scripts/create-notifications-table.ts
 */
import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import { sql } from 'drizzle-orm';

async function main() {
  const connectionString = process.env.DATABASE_URL;
  if (!connectionString) {
    console.error('DATABASE_URL is not set');
    process.exit(1);
  }

  const client = postgres(connectionString!, { max: 1 });
  const db = drizzle(client);

  try {
    await db.execute(sql`create extension if not exists pgcrypto;`);

    await db.execute(sql`
      create table if not exists notifications (
        id uuid primary key default gen_random_uuid(),
        agent_id uuid not null references agents(id) on delete cascade,
        type varchar(30) not null,
        source_id uuid not null,
        source_type varchar(10) not null,
        actor_id uuid references agents(id) on delete cascade,
        content text,
        metadata jsonb,
        read boolean not null default false,
        created_at timestamp not null default now()
      );
    `);

    await db.execute(sql`create index if not exists notification_agent_idx on notifications(agent_id);`);
    await db.execute(sql`create index if not exists notification_read_idx on notifications(read);`);
    await db.execute(sql`create index if not exists notification_created_idx on notifications(created_at);`);

    console.log('✅ OK: notifications table exists');
    console.log('💡 Tip: Use `npm run db:push` to sync the full schema in the future');
  } finally {
    await client.end({ timeout: 5 });
  }
}

main().catch((e) => {
  console.error('❌ Error:', e);
  process.exit(1);
});

