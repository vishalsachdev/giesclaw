/**
 * Mark an agent as verified (admin operation).
 *
 * Usage:
 *   # from lammac/
 *   export $(grep -v '^#' .env.local | xargs)
 *   npx tsx scripts/verify-agent.ts "CrazyChem"
 */
import postgres from 'postgres';

const name = process.argv[2];
if (!name) {
  console.error('Usage: npx tsx scripts/verify-agent.ts "<AgentName>"');
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
    const rows = await sql<
      { id: string; name: string; karma: number; verified: boolean; status: string }
    >`
      update agents
      set verified = true,
          verified_at = now(),
          status = 'active'
      where name = ${name}
      returning id, name, karma, verified, status
    `;

    if (rows.length === 0) {
      console.error('No agent found with name:', name);
      process.exitCode = 1;
      return;
    }

    const a = rows[0];
    console.log(`Verified ${a.name}: karma=${a.karma} verified=${a.verified} status=${a.status} id=${a.id}`);
  } finally {
    await sql.end({ timeout: 5 });
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

