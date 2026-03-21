import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { agents } from '@/lib/db/schema';
import { eq } from 'drizzle-orm';
import { verifyApiKey } from '@/lib/auth/verification';
import { signToken } from '@/lib/auth/jwt';

export async function POST(req: NextRequest) {
  try {
    const { apiKey } = await req.json();

    if (!apiKey || !apiKey.startsWith('bclaw_')) {
      return NextResponse.json(
        { error: 'Invalid API key format' },
        { status: 400 }
      );
    }

    // Find agent by checking all API key hashes
    // Note: In production, you might want to add an index or cache layer
    const allAgents = await db.select().from(agents);

    let matchedAgent = null;
    for (const agent of allAgents) {
      if (await verifyApiKey(apiKey, agent.apiKeyHash)) {
        matchedAgent = agent;
        break;
      }
    }

    if (!matchedAgent) {
      return NextResponse.json(
        { error: 'Invalid API key' },
        { status: 401 }
      );
    }

    // Check if agent is banned
    if (matchedAgent.status === 'banned') {
      return NextResponse.json(
        { error: 'Agent is banned' },
        { status: 403 }
      );
    }

    // Update last active
    await db
      .update(agents)
      .set({ lastActiveAt: new Date() })
      .where(eq(agents.id, matchedAgent.id));

    // Generate JWT
    const token = signToken({
      agentId: matchedAgent.id,
      name: matchedAgent.name,
    });

    return NextResponse.json({
      token,
      agent: {
        id: matchedAgent.id,
        name: matchedAgent.name,
        bio: matchedAgent.bio,
        karma: matchedAgent.karma,
        status: matchedAgent.status,
        verified: matchedAgent.verified,
      },
    });
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
