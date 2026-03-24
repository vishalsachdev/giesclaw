import { NextRequest, NextResponse } from 'next/server';
import { randomBytes } from 'crypto';
import bcrypt from 'bcrypt';
import { db } from '@/lib/db/client';
import { magicLinks } from '@/lib/db/sos-schema';
import { humans } from '@/lib/db/schema';
import { eq, and, isNull } from 'drizzle-orm';
import { signToken } from '@/lib/auth/jwt';

export async function GET(req: NextRequest) {
  try {
    const token = req.nextUrl.searchParams.get('token');
    if (!token) {
      return NextResponse.json({ error: 'Token required' }, { status: 400 });
    }
    const [link] = await db.select().from(magicLinks)
      .where(and(eq(magicLinks.token, token), isNull(magicLinks.usedAt))).limit(1);
    if (!link) {
      return NextResponse.json({ error: 'Invalid or expired link' }, { status: 400 });
    }
    if (new Date() > link.expiresAt) {
      return NextResponse.json({ error: 'Link has expired' }, { status: 400 });
    }
    let human = await db.query.humans.findFirst({ where: eq(humans.email, link.email) });
    if (!human) {
      const dummyHash = await bcrypt.hash(randomBytes(32).toString('hex'), 10);
      const nameFromEmail = link.email.split('@')[0].replace(/[^a-zA-Z0-9-]/g, '-');
      const [newHuman] = await db.insert(humans).values({
        name: nameFromEmail, email: link.email, passwordHash: dummyHash,
      }).returning();
      human = newHuman;
    }
    await db.update(magicLinks).set({ usedAt: new Date(), humanId: human.id }).where(eq(magicLinks.id, link.id));
    const jwt = signToken({ humanId: human.id, name: human.name });
    return NextResponse.json({ token: jwt, human: { id: human.id, name: human.name } });
  } catch (error) {
    console.error('Magic link verify error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
