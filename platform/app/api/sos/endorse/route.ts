import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { endorsements } from '@/lib/db/sos-schema';
import { getTokenFromRequest, verifyToken } from '@/lib/auth/jwt';
import { eq, and, sql } from 'drizzle-orm';

export async function POST(req: NextRequest) {
  try {
    const token = getTokenFromRequest(req);
    if (!token) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    const payload = verifyToken(token);
    if (!payload?.humanId) return NextResponse.json({ error: 'Only faculty can endorse' }, { status: 403 });
    const { postId } = await req.json();
    if (!postId) return NextResponse.json({ error: 'postId required' }, { status: 400 });

    const existing = await db.select().from(endorsements)
      .where(and(eq(endorsements.postId, postId), eq(endorsements.humanId, payload.humanId))).limit(1);

    if (existing.length > 0) {
      await db.delete(endorsements).where(eq(endorsements.id, existing[0].id));
      const [countResult] = await db.select({ count: sql<number>`count(*)` })
        .from(endorsements).where(eq(endorsements.postId, postId));
      return NextResponse.json({ endorsed: false, count: Number(countResult.count) });
    }

    await db.insert(endorsements).values({ postId, humanId: payload.humanId });
    const [countResult] = await db.select({ count: sql<number>`count(*)` })
      .from(endorsements).where(eq(endorsements.postId, postId));
    return NextResponse.json({ endorsed: true, count: Number(countResult.count) });
  } catch (error) {
    console.error('Endorse error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
