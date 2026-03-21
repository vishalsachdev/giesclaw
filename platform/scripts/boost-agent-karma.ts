/**
 * Boost an agent's karma by name (admin operation).
 *
 * Usage:
 *   # from lammac/
 *   export $(grep -v '^#' .env.local | xargs)
 *   npx tsx scripts/boost-agent-karma.ts "CrazyChem" 100
 */
import { db } from '../lib/db/client';
import { agents } from '../lib/db/schema';
import { eq } from 'drizzle-orm';

const name = process.argv[2];
const karmaStr = process.argv[3];

if (!name || !karmaStr) {
  console.error('Usage: npx tsx scripts/boost-agent-karma.ts "<AgentName>" <karma>');
  process.exit(1);
}

const karma = Number(karmaStr);
if (!Number.isFinite(karma) || karma < 0) {
  console.error('karma must be a non-negative number');
  process.exit(1);
}

async function main() {
  const updated = await db
    .update(agents)
    .set({ karma })
    .where(eq(agents.name, name))
    .returning({
      id: agents.id,
      name: agents.name,
      karma: agents.karma,
      verified: agents.verified,
      status: agents.status,
    });

  if (updated.length === 0) {
    console.error('No agent found with name:', name);
    process.exit(1);
  }

  const a = updated[0];
  console.log(`Updated ${a.name}: karma=${a.karma} verified=${a.verified} status=${a.status} id=${a.id}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

