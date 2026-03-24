import { NextRequest, NextResponse } from 'next/server';
import { randomBytes, randomUUID } from 'crypto';
import { db } from '@/lib/db/client';
import { magicLinks } from '@/lib/db/sos-schema';

export async function POST(req: NextRequest) {
  try {
    const { email } = await req.json();
    if (!email || !email.endsWith('@illinois.edu')) {
      return NextResponse.json({ error: 'Please use your @illinois.edu email address' }, { status: 400 });
    }
    const token = randomUUID() + randomBytes(32).toString('hex');
    const expiresAt = new Date(Date.now() + 60 * 60 * 1000);
    await db.insert(magicLinks).values({ email: email.toLowerCase(), token, expiresAt });
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://giesclaw.illinihunt.org';
    console.log(`[SOS Magic Link] ${email}: ${baseUrl}/sos/join?token=${token}`);
    return NextResponse.json({ message: 'Magic link sent to your email' });
  } catch (error) {
    console.error('Magic link request error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
