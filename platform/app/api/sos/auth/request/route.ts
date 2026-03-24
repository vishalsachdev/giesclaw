import { NextRequest, NextResponse } from 'next/server';
import { randomBytes, randomUUID } from 'crypto';
import { db } from '@/lib/db/client';
import { magicLinks } from '@/lib/db/sos-schema';
import { sendMagicLinkEmail } from '@/lib/email/send';

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
    const magicUrl = `${baseUrl}/sos/join?token=${token}`;

    const emailSent = await sendMagicLinkEmail(email.toLowerCase(), magicUrl);

    // Return magicUrl as fallback if email fails (for testing/demo)
    return NextResponse.json({
      message: emailSent ? 'Check your email for the login link.' : 'Check your email (or use the link below).',
      ...(!emailSent && { magicUrl }),
    });
  } catch (error) {
    console.error('Magic link request error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
