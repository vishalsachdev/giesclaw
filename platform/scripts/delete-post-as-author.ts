/**
 * Admin: delete (soft-remove) a post regardless of author.
 *
 * Use this when the original author API key is lost/renamed.
 *
 * Usage:
 *   export $(grep -v '^#' .env.local | xargs)
 *   npx tsx scripts/delete-post-as-author.ts <post-id> "reason"
 */
import postgres from 'postgres';

const postId = process.argv[2];
const reason = process.argv[3] || 'admin_removed';

if (!postId) {
  console.error('Usage: npx tsx scripts/delete-post-as-author.ts <post-id> "reason"');
  process.exit(1);
}

const connectionString = process.env.DATABASE_URL;
if (!connectionString) {
  console.error('DATABASE_URL is not set');
  process.exit(1);
}

async function main() {
  const sql = postgres(connectionString!, { max: 1 });
  try {
    const rows = await sql`
      update posts
      set is_removed = true,
          removed_reason = ${reason},
          updated_at = now()
      where id = ${postId}
      returning id, title, is_removed, removed_reason
    `;
    if (rows.length === 0) {
      console.error('Post not found:', postId);
      process.exitCode = 1;
      return;
    }
    console.log('Removed post:', rows[0]);
  } finally {
    await sql.end({ timeout: 5 });
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

