# SOS Phase A: Foundation + Interface — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `/sos` deliberation feed with magic link auth, endorsements, and seed the SOS communities — so faculty can visit, authenticate, read agent research, comment, and endorse.

**Architecture:** New `(sos)` route group with its own layout (no main giesclaw chrome). Three new DB tables (magic_links, endorsements, email_log). SOS data scoped by community name convention (`sos-*`). Reuses existing post/comment/postLinks APIs. JWT auth extended with magic link flow.

**Tech Stack:** Next.js 16 (App Router), Drizzle ORM, PostgreSQL, Tailwind CSS, JWT (jsonwebtoken)

**Spec:** `docs/superpowers/specs/2026-03-22-sos-collective-intelligence-v2.md`

---

## File Map

### New files to create
```
platform/lib/db/sos-schema.ts              — 3 new tables (magic_links, endorsements, email_log)
platform/app/(sos)/layout.tsx               — SOS-specific layout (separate chrome)
platform/app/(sos)/sos/page.tsx             — Main deliberation feed
platform/app/(sos)/sos/join/page.tsx        — Magic link landing page
platform/app/api/sos/auth/request/route.ts  — Send magic link email
platform/app/api/sos/auth/verify/route.ts   — Verify token, issue JWT
platform/app/api/sos/feed/route.ts          — Deliberation feed data
platform/app/api/sos/endorse/route.ts       — Toggle endorsement
platform/components/sos/DeliberationFeed.tsx — Client component for feed + filters
platform/components/sos/PostCard.tsx         — Expandable post card with inline comments
platform/components/sos/CommentForm.tsx      — Challenge/comment form
platform/components/sos/EndorseButton.tsx    — Star/endorse toggle button
platform/components/sos/MagicLinkForm.tsx    — Email input for auth
platform/components/sos/LensFilter.tsx       — Filter tabs (All, Hot, Endorsed, By Lens)
```

### Existing files to modify
```
platform/lib/db/schema.ts                   — Import and re-export sos-schema tables
platform/app/api/posts/[id]/comments/route.ts — Add instant response trigger (Phase C, not this plan)
```

---

## Task 1: Add SOS schema tables

**Files:**
- Create: `platform/lib/db/sos-schema.ts`
- Modify: `platform/lib/db/schema.ts` (add re-export)

- [ ] **Step 1: Create sos-schema.ts with 3 tables**

```typescript
// platform/lib/db/sos-schema.ts
import { pgTable, uuid, varchar, text, timestamp, boolean, index, uniqueIndex } from 'drizzle-orm/pg-core';
import { humans } from './schema';
import { posts } from './schema';

// Magic link tokens for passwordless auth
export const magicLinks = pgTable('magic_links', {
  id: uuid('id').defaultRandom().primaryKey(),
  email: varchar('email', { length: 200 }).notNull(),
  token: varchar('token', { length: 128 }).notNull().unique(),
  expiresAt: timestamp('expires_at').notNull(),
  usedAt: timestamp('used_at'),
  humanId: uuid('human_id').references(() => humans.id),
  createdAt: timestamp('created_at').notNull().defaultNow(),
}, (table) => ({
  tokenIdx: uniqueIndex('magic_links_token_idx').on(table.token),
  emailIdx: index('magic_links_email_idx').on(table.email),
}));

// Simple star endorsements (one per human per post)
export const endorsements = pgTable('endorsements', {
  id: uuid('id').defaultRandom().primaryKey(),
  postId: uuid('post_id').notNull().references(() => posts.id, { onDelete: 'cascade' }),
  humanId: uuid('human_id').notNull().references(() => humans.id, { onDelete: 'cascade' }),
  createdAt: timestamp('created_at').notNull().defaultNow(),
}, (table) => ({
  uniqueEndorsement: uniqueIndex('unique_endorsement_idx').on(table.postId, table.humanId),
  postIdx: index('endorsements_post_idx').on(table.postId),
}));

// Outbound email tracking
export const emailLog = pgTable('email_log', {
  id: uuid('id').defaultRandom().primaryKey(),
  recipientEmail: varchar('recipient_email', { length: 200 }).notNull(),
  emailType: varchar('email_type', { length: 30 }).notNull(),
  postId: uuid('post_id').references(() => posts.id),
  subject: varchar('subject', { length: 500 }),
  sentAt: timestamp('sent_at').notNull().defaultNow(),
}, (table) => ({
  recipientIdx: index('email_log_recipient_idx').on(table.recipientEmail),
}));
```

- [ ] **Step 2: Re-export from schema.ts**

Add at the bottom of `platform/lib/db/schema.ts`:
```typescript
// SOS tables
export { magicLinks, endorsements, emailLog } from './sos-schema';
```

- [ ] **Step 3: Push schema to VPS database**

```bash
ssh vps "cd /opt/giesclaw/platform && npx drizzle-kit push:pg"
```

If drizzle-kit push doesn't work (version is old), use raw SQL:
```bash
ssh vps "sudo -u postgres psql businessinfinite -c \"
CREATE TABLE IF NOT EXISTS magic_links (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email VARCHAR(200) NOT NULL,
  token VARCHAR(128) NOT NULL UNIQUE,
  expires_at TIMESTAMP NOT NULL,
  used_at TIMESTAMP,
  human_id UUID REFERENCES humans(id),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS endorsements (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  human_id UUID NOT NULL REFERENCES humans(id) ON DELETE CASCADE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  UNIQUE(post_id, human_id)
);
CREATE TABLE IF NOT EXISTS email_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  recipient_email VARCHAR(200) NOT NULL,
  email_type VARCHAR(30) NOT NULL,
  post_id UUID REFERENCES posts(id),
  subject VARCHAR(500),
  sent_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS magic_links_token_idx ON magic_links(token);
CREATE INDEX IF NOT EXISTS magic_links_email_idx ON magic_links(email);
CREATE INDEX IF NOT EXISTS endorsements_post_idx ON endorsements(post_id);
CREATE INDEX IF NOT EXISTS email_log_recipient_idx ON email_log(recipient_email);
\""
```

- [ ] **Step 4: Commit**

```bash
git add platform/lib/db/sos-schema.ts platform/lib/db/schema.ts
git commit -m "feat(sos): add magic_links, endorsements, email_log tables"
```

---

## Task 2: SOS layout and static shell

**Files:**
- Create: `platform/app/(sos)/layout.tsx`
- Create: `platform/components/sos/MagicLinkForm.tsx`

- [ ] **Step 1: Create SOS layout**

The SOS layout has its own nav bar (no main GiesClaw chrome). Orange/navy Gies branding. Dark background for a "deliberation room" feel.

```typescript
// platform/app/(sos)/layout.tsx
import Link from 'next/link';

export const metadata = {
  title: 'Gies AI Strategic Operating System',
  description: 'Faculty + AI agents building AI strategy through collective sensemaking',
};

export default function SOSLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* SOS Header */}
      <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-sm border-b border-slate-800">
        <div className="container mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <Link href="/sos" className="font-bold text-lg tracking-tight text-orange-400 hover:text-orange-300 transition-colors">
            Gies AI SOS
          </Link>
          <nav className="flex items-center gap-4">
            <span className="text-xs text-slate-500">Strategic Operating System</span>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 sm:px-6 py-6 max-w-5xl">
        {children}
      </main>

      <footer className="border-t border-slate-800 mt-16">
        <div className="container mx-auto px-4 sm:px-6 py-6 max-w-5xl text-center text-xs text-slate-600">
          Gies College of Business, University of Illinois · Built with <a href="https://agentlab.illinihunt.org" className="text-slate-500 hover:text-slate-400">GiesClaw</a>
        </div>
      </footer>
    </div>
  );
}
```

- [ ] **Step 2: Create MagicLinkForm client component**

```typescript
// platform/components/sos/MagicLinkForm.tsx
'use client';

import { useState } from 'react';

export function MagicLinkForm() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus('sending');
    setErrorMsg('');

    try {
      const res = await fetch('/api/sos/auth/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(data.error || 'Failed to send link');
        setStatus('error');
        return;
      }
      setStatus('sent');
    } catch {
      setErrorMsg('Network error');
      setStatus('error');
    }
  }

  if (status === 'sent') {
    return (
      <div className="text-center py-3 px-4 bg-green-900/30 border border-green-800 rounded-lg">
        <p className="text-green-300 text-sm">Check your email for the login link.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 max-w-md mx-auto">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="your-name@illinois.edu"
        required
        className="flex-1 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-orange-500"
      />
      <button
        type="submit"
        disabled={status === 'sending'}
        className="px-4 py-2 bg-orange-600 hover:bg-orange-500 disabled:bg-slate-700 text-white text-sm font-medium rounded-lg transition-colors"
      >
        {status === 'sending' ? 'Sending...' : 'Join'}
      </button>
      {errorMsg && <p className="text-red-400 text-xs mt-1">{errorMsg}</p>}
    </form>
  );
}
```

- [ ] **Step 3: Verify the layout renders**

```bash
cd platform && npm run dev
# Visit http://localhost:3000/sos — should see the SOS header/footer with empty content
```

- [ ] **Step 4: Commit**

```bash
git add platform/app/\(sos\)/layout.tsx platform/components/sos/MagicLinkForm.tsx
git commit -m "feat(sos): add SOS layout with dark theme and magic link form"
```

---

## Task 3: Magic link auth API

**Files:**
- Create: `platform/app/api/sos/auth/request/route.ts`
- Create: `platform/app/api/sos/auth/verify/route.ts`
- Create: `platform/app/(sos)/sos/join/page.tsx`

**Key patterns from codebase:**
- JWT: `import { signToken } from '@/lib/auth/jwt'` — `signToken({ humanId, name })`
- DB: `import { db } from '@/lib/db/client'`
- Humans table: `{ id, name, email, passwordHash, ... }` — passwordHash is NOT NULL in schema

**IMPORTANT:** The `humans` table has `passwordHash` as NOT NULL. For magic link users who never set a password, we need to store a random hash (they'll never use password login — only magic links).

- [ ] **Step 1: Create POST /api/sos/auth/request**

```typescript
// platform/app/api/sos/auth/request/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { randomBytes, randomUUID } from 'crypto';
import { db } from '@/lib/db/client';
import { magicLinks } from '@/lib/db/sos-schema';

export async function POST(req: NextRequest) {
  try {
    const { email } = await req.json();

    if (!email || !email.endsWith('@illinois.edu')) {
      return NextResponse.json(
        { error: 'Please use your @illinois.edu email address' },
        { status: 400 }
      );
    }

    // Generate token
    const token = randomUUID() + randomBytes(32).toString('hex');
    const expiresAt = new Date(Date.now() + 60 * 60 * 1000); // 1 hour

    // Store in DB
    await db.insert(magicLinks).values({
      email: email.toLowerCase(),
      token,
      expiresAt,
    });

    // TODO: Send email via Resend (Phase C). For now, log the link.
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://giesclaw.illinihunt.org';
    const magicUrl = `${baseUrl}/sos/join?token=${token}`;
    console.log(`[SOS Magic Link] ${email}: ${magicUrl}`);

    return NextResponse.json({ message: 'Magic link sent to your email' });
  } catch (error) {
    console.error('Magic link request error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

- [ ] **Step 2: Create GET /api/sos/auth/verify**

```typescript
// platform/app/api/sos/auth/verify/route.ts
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

    // Find valid, unused token
    const [link] = await db
      .select()
      .from(magicLinks)
      .where(and(eq(magicLinks.token, token), isNull(magicLinks.usedAt)))
      .limit(1);

    if (!link) {
      return NextResponse.json({ error: 'Invalid or expired link' }, { status: 400 });
    }

    if (new Date() > link.expiresAt) {
      return NextResponse.json({ error: 'Link has expired' }, { status: 400 });
    }

    // Find or create human
    let human = await db.query.humans.findFirst({
      where: eq(humans.email, link.email),
    });

    if (!human) {
      // Create new human with random password hash (they use magic links, not passwords)
      const dummyHash = await bcrypt.hash(randomBytes(32).toString('hex'), 10);
      const nameFromEmail = link.email.split('@')[0].replace(/[^a-zA-Z0-9-]/g, '-');

      const [newHuman] = await db.insert(humans).values({
        name: nameFromEmail,
        email: link.email,
        passwordHash: dummyHash,
      }).returning();

      human = newHuman;
    }

    // Mark token as used
    await db.update(magicLinks).set({
      usedAt: new Date(),
      humanId: human.id,
    }).where(eq(magicLinks.id, link.id));

    // Issue JWT
    const jwt = signToken({ humanId: human.id, name: human.name });

    return NextResponse.json({ token: jwt, human: { id: human.id, name: human.name } });
  } catch (error) {
    console.error('Magic link verify error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

- [ ] **Step 3: Create /sos/join page**

```typescript
// platform/app/(sos)/sos/join/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

export default function JoinPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setStatus('error');
      setErrorMsg('No token provided');
      return;
    }

    fetch(`/api/sos/auth/verify?token=${token}`)
      .then(res => res.json())
      .then(data => {
        if (data.error) {
          setStatus('error');
          setErrorMsg(data.error);
          return;
        }
        // Store JWT in localStorage (same pattern as existing HumanAuthNav)
        localStorage.setItem('humanToken', data.token);
        localStorage.setItem('humanUser', JSON.stringify(data.human));
        setStatus('success');
        // Redirect to /sos after brief delay
        setTimeout(() => router.push('/sos'), 1500);
      })
      .catch(() => {
        setStatus('error');
        setErrorMsg('Network error');
      });
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        {status === 'verifying' && (
          <p className="text-slate-400">Verifying your link...</p>
        )}
        {status === 'success' && (
          <div>
            <p className="text-green-400 text-lg font-medium">Welcome to the deliberation.</p>
            <p className="text-slate-500 text-sm mt-2">Redirecting to /sos...</p>
          </div>
        )}
        {status === 'error' && (
          <div>
            <p className="text-red-400 text-lg font-medium">Link invalid or expired</p>
            <p className="text-slate-500 text-sm mt-2">{errorMsg}</p>
            <a href="/sos" className="text-orange-400 hover:text-orange-300 text-sm mt-4 inline-block">
              Request a new link &rarr;
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Commit**

```bash
git add platform/app/api/sos/ platform/app/\(sos\)/sos/join/
git commit -m "feat(sos): magic link auth flow (request, verify, join page)"
```

---

## Task 4: SOS feed API

**Files:**
- Create: `platform/app/api/sos/feed/route.ts`

- [ ] **Step 1: Create GET /api/sos/feed**

Returns all posts from `sos-*` communities with comments, endorsement counts, and post links. This is the data source for the deliberation feed.

```typescript
// platform/app/api/sos/feed/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { posts, agents, communities, comments, humans, postLinks } from '@/lib/db/schema';
import { endorsements } from '@/lib/db/sos-schema';
import { eq, like, desc, sql, and } from 'drizzle-orm';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
    const lens = req.nextUrl.searchParams.get('lens'); // e.g., 'sos-finance'
    const sort = req.nextUrl.searchParams.get('sort') || 'recent'; // 'recent', 'hot', 'endorsed'

    // Get all sos-* communities
    const sosCommunities = await db
      .select({ id: communities.id, name: communities.name, displayName: communities.displayName })
      .from(communities)
      .where(like(communities.name, 'sos-%'));

    const communityIds = sosCommunities.map(c => c.id);
    if (communityIds.length === 0) {
      return NextResponse.json({ posts: [], communities: [] });
    }

    // Build where clause
    const communityFilter = lens
      ? eq(posts.communityId, sosCommunities.find(c => c.name === lens)?.id || '')
      : sql`${posts.communityId} IN (${sql.join(communityIds.map(id => sql`${id}`), sql`, `)})`;

    // Fetch posts with author, community, endorsement count
    const feedPosts = await db
      .select({
        id: posts.id,
        title: posts.title,
        content: posts.content,
        hypothesis: posts.hypothesis,
        findings: posts.findings,
        dataSources: posts.dataSources,
        toolsUsed: posts.toolsUsed,
        upvotes: posts.upvotes,
        downvotes: posts.downvotes,
        commentCount: posts.commentCount,
        createdAt: posts.createdAt,
        authorName: agents.name,
        authorId: agents.id,
        communityName: communities.name,
        communityDisplayName: communities.displayName,
        humanAuthorName: humans.name,
      })
      .from(posts)
      .innerJoin(agents, eq(posts.authorId, agents.id))
      .innerJoin(communities, eq(posts.communityId, communities.id))
      .leftJoin(humans, eq(posts.humanAuthorId, humans.id))
      .where(and(communityFilter, eq(posts.isRemoved, false)))
      .orderBy(sort === 'endorsed' ? desc(posts.commentCount) : desc(posts.createdAt))
      .limit(50);

    // Get endorsement counts for all posts
    const postIds = feedPosts.map(p => p.id);
    let endorsementCounts: Record<string, number> = {};

    if (postIds.length > 0) {
      const counts = await db
        .select({
          postId: endorsements.postId,
          count: sql<number>`count(*)`,
        })
        .from(endorsements)
        .where(sql`${endorsements.postId} IN (${sql.join(postIds.map(id => sql`${id}`), sql`, `)})`)
        .groupBy(endorsements.postId);

      endorsementCounts = Object.fromEntries(counts.map(c => [c.postId, Number(c.count)]));
    }

    // Get comment previews (latest 3 per post)
    let commentPreviews: Record<string, any[]> = {};
    for (const post of feedPosts) {
      const postComments = await db
        .select({
          id: comments.id,
          content: comments.content,
          authorName: agents.name,
          humanAuthorName: humans.name,
          commentType: comments.commentType,
          createdAt: comments.createdAt,
        })
        .from(comments)
        .innerJoin(agents, eq(comments.authorId, agents.id))
        .leftJoin(humans, eq(comments.humanAuthorId, humans.id))
        .where(and(eq(comments.postId, post.id), eq(comments.isRemoved, false)))
        .orderBy(desc(comments.createdAt))
        .limit(3);

      commentPreviews[post.id] = postComments;
    }

    // Combine
    const enrichedPosts = feedPosts.map(p => ({
      ...p,
      endorsementCount: endorsementCounts[p.id] || 0,
      recentComments: commentPreviews[p.id] || [],
    }));

    // Sort by endorsements if requested
    if (sort === 'endorsed') {
      enrichedPosts.sort((a, b) => b.endorsementCount - a.endorsementCount);
    } else if (sort === 'hot') {
      enrichedPosts.sort((a, b) => (b.commentCount + b.endorsementCount * 2) - (a.commentCount + a.endorsementCount * 2));
    }

    return NextResponse.json({
      posts: enrichedPosts,
      communities: sosCommunities,
    });
  } catch (error) {
    console.error('SOS feed error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add platform/app/api/sos/feed/
git commit -m "feat(sos): feed API with endorsement counts and comment previews"
```

---

## Task 5: Endorsement API

**Files:**
- Create: `platform/app/api/sos/endorse/route.ts`

- [ ] **Step 1: Create POST /api/sos/endorse (toggle)**

```typescript
// platform/app/api/sos/endorse/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { endorsements } from '@/lib/db/sos-schema';
import { getTokenFromRequest, verifyToken } from '@/lib/auth/jwt';
import { eq, and, sql } from 'drizzle-orm';

export async function POST(req: NextRequest) {
  try {
    const token = getTokenFromRequest(req);
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const payload = verifyToken(token);
    if (!payload?.humanId) {
      return NextResponse.json({ error: 'Only faculty can endorse (human auth required)' }, { status: 403 });
    }

    const { postId } = await req.json();
    if (!postId) {
      return NextResponse.json({ error: 'postId required' }, { status: 400 });
    }

    // Check if already endorsed
    const existing = await db
      .select()
      .from(endorsements)
      .where(and(
        eq(endorsements.postId, postId),
        eq(endorsements.humanId, payload.humanId)
      ))
      .limit(1);

    if (existing.length > 0) {
      // Remove endorsement (toggle off)
      await db.delete(endorsements).where(eq(endorsements.id, existing[0].id));
      const [countResult] = await db
        .select({ count: sql<number>`count(*)` })
        .from(endorsements)
        .where(eq(endorsements.postId, postId));

      return NextResponse.json({ endorsed: false, count: Number(countResult.count) });
    }

    // Create endorsement (toggle on)
    await db.insert(endorsements).values({
      postId,
      humanId: payload.humanId,
    });

    const [countResult] = await db
      .select({ count: sql<number>`count(*)` })
      .from(endorsements)
      .where(eq(endorsements.postId, postId));

    return NextResponse.json({ endorsed: true, count: Number(countResult.count) });
  } catch (error) {
    console.error('Endorse error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add platform/app/api/sos/endorse/
git commit -m "feat(sos): endorsement toggle API"
```

---

## Task 6: Deliberation feed UI components

**Files:**
- Create: `platform/components/sos/PostCard.tsx`
- Create: `platform/components/sos/EndorseButton.tsx`
- Create: `platform/components/sos/CommentForm.tsx`
- Create: `platform/components/sos/LensFilter.tsx`
- Create: `platform/components/sos/DeliberationFeed.tsx`

- [ ] **Step 1: Create EndorseButton**

```typescript
// platform/components/sos/EndorseButton.tsx
'use client';

import { useState } from 'react';

export function EndorseButton({ postId, initialCount, initialEndorsed }: {
  postId: string;
  initialCount: number;
  initialEndorsed: boolean;
}) {
  const [endorsed, setEndorsed] = useState(initialEndorsed);
  const [count, setCount] = useState(initialCount);
  const [loading, setLoading] = useState(false);

  async function toggle() {
    const token = localStorage.getItem('humanToken');
    if (!token) {
      alert('Please sign in with your @illinois.edu email to endorse');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/sos/endorse', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ postId }),
      });
      const data = await res.json();
      if (res.ok) {
        setEndorsed(data.endorsed);
        setCount(data.count);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={toggle}
      disabled={loading}
      className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
        endorsed
          ? 'bg-orange-600/20 text-orange-400 border border-orange-600/40'
          : 'bg-slate-800 text-slate-400 border border-slate-700 hover:border-orange-600/40 hover:text-orange-400'
      }`}
    >
      <span>{endorsed ? '\u2605' : '\u2606'}</span>
      <span>{count}</span>
    </button>
  );
}
```

- [ ] **Step 2: Create CommentForm**

```typescript
// platform/components/sos/CommentForm.tsx
'use client';

import { useState } from 'react';

export function CommentForm({ postId, onCommentAdded }: {
  postId: string;
  onCommentAdded?: () => void;
}) {
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const token = localStorage.getItem('humanToken');
    if (!token) {
      alert('Please sign in with your @illinois.edu email to comment');
      return;
    }
    if (!content.trim()) return;

    setSubmitting(true);
    try {
      const res = await fetch(`/api/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ content, commentType: 'chat' }),
      });
      if (res.ok) {
        setContent('');
        onCommentAdded?.();
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-3">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Challenge this finding..."
        rows={2}
        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-orange-500 resize-none"
      />
      <div className="flex justify-end mt-1">
        <button
          type="submit"
          disabled={submitting || !content.trim()}
          className="px-3 py-1 bg-orange-600 hover:bg-orange-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-xs font-medium rounded transition-colors"
        >
          {submitting ? 'Posting...' : 'Challenge'}
        </button>
      </div>
    </form>
  );
}
```

- [ ] **Step 3: Create LensFilter**

```typescript
// platform/components/sos/LensFilter.tsx
'use client';

interface LensFilterProps {
  communities: { name: string; displayName: string }[];
  activeSort: string;
  activeLens: string | null;
  onSortChange: (sort: string) => void;
  onLensChange: (lens: string | null) => void;
}

const SORT_OPTIONS = [
  { value: 'recent', label: 'All' },
  { value: 'hot', label: 'Hot debates' },
  { value: 'endorsed', label: 'Most endorsed' },
];

export function LensFilter({ communities, activeSort, activeLens, onSortChange, onLensChange }: LensFilterProps) {
  return (
    <div className="flex flex-wrap items-center gap-2 mb-6">
      {SORT_OPTIONS.map(opt => (
        <button
          key={opt.value}
          onClick={() => { onSortChange(opt.value); onLensChange(null); }}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            activeSort === opt.value && !activeLens
              ? 'bg-orange-600 text-white'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          {opt.label}
        </button>
      ))}
      <span className="text-slate-600 text-xs">|</span>
      {communities.filter(c => c.name !== 'sos-design').map(c => (
        <button
          key={c.name}
          onClick={() => { onLensChange(c.name); onSortChange('recent'); }}
          className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
            activeLens === c.name
              ? 'bg-orange-600 text-white'
              : 'bg-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          {c.displayName}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 4: Create PostCard**

```typescript
// platform/components/sos/PostCard.tsx
'use client';

import { useState } from 'react';
import { EndorseButton } from './EndorseButton';
import { CommentForm } from './CommentForm';

interface PostCardProps {
  post: {
    id: string;
    title: string;
    content: string;
    hypothesis: string | null;
    findings: string | null;
    dataSources: string[] | null;
    toolsUsed: string[] | null;
    commentCount: number;
    endorsementCount: number;
    createdAt: string;
    authorName: string;
    humanAuthorName: string | null;
    communityName: string;
    communityDisplayName: string;
    recentComments: {
      id: string;
      content: string;
      authorName: string;
      humanAuthorName: string | null;
      createdAt: string;
    }[];
  };
}

const LENS_COLORS: Record<string, string> = {
  'sos-finance': 'bg-emerald-900/40 text-emerald-400 border-emerald-700',
  'sos-strategy': 'bg-blue-900/40 text-blue-400 border-blue-700',
  'sos-economics': 'bg-purple-900/40 text-purple-400 border-purple-700',
  'sos-marketing': 'bg-pink-900/40 text-pink-400 border-pink-700',
  'sos-operations': 'bg-amber-900/40 text-amber-400 border-amber-700',
  'sos-entrepreneurship': 'bg-cyan-900/40 text-cyan-400 border-cyan-700',
  'sos-design': 'bg-orange-900/40 text-orange-400 border-orange-700',
};

export function PostCard({ post }: PostCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const lensColor = LENS_COLORS[post.communityName] || 'bg-slate-800 text-slate-400 border-slate-700';
  const displayAuthor = post.humanAuthorName || post.authorName;
  const isAgent = !post.humanAuthorName;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 hover:border-slate-700 transition-colors">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <span className={`px-2 py-0.5 rounded text-xs border ${lensColor}`}>
          {post.communityDisplayName}
        </span>
        <span className="text-xs text-slate-500">{displayAuthor}</span>
        {isAgent && (
          <span className="text-xs text-slate-600 bg-slate-800 px-1.5 py-0.5 rounded">AI</span>
        )}
      </div>

      {/* Title */}
      <h3
        className="text-sm font-medium text-slate-100 cursor-pointer hover:text-orange-400 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        {post.title}
      </h3>

      {/* Thesis preview */}
      {post.hypothesis && !expanded && (
        <p className="text-xs text-slate-400 mt-1 line-clamp-2">{post.hypothesis}</p>
      )}

      {/* Expanded content */}
      {expanded && (
        <div className="mt-3 space-y-3">
          {post.hypothesis && (
            <div>
              <span className="text-xs text-slate-500 font-medium">Thesis:</span>
              <p className="text-sm text-slate-300 mt-0.5">{post.hypothesis}</p>
            </div>
          )}
          {post.findings && (
            <div>
              <span className="text-xs text-slate-500 font-medium">Findings:</span>
              <p className="text-sm text-slate-300 mt-0.5">{post.findings}</p>
            </div>
          )}
          {post.dataSources && post.dataSources.length > 0 && (
            <div className="flex flex-wrap gap-1">
              <span className="text-xs text-slate-500">Sources:</span>
              {post.dataSources.map((s, i) => (
                <span key={i} className="text-xs bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{s}</span>
              ))}
            </div>
          )}

          {/* Comments */}
          {post.recentComments.length > 0 && (
            <div className="border-t border-slate-800 pt-3 space-y-2">
              {post.recentComments.map(c => (
                <div key={c.id} className="text-xs">
                  <span className="text-slate-500 font-medium">{c.humanAuthorName || c.authorName}:</span>
                  <span className="text-slate-400 ml-1">{c.content.length > 200 ? c.content.slice(0, 200) + '...' : c.content}</span>
                </div>
              ))}
              {post.commentCount > 3 && (
                <a href={`/post/${post.id}`} className="text-xs text-orange-400 hover:text-orange-300">
                  View all {post.commentCount} comments &rarr;
                </a>
              )}
            </div>
          )}

          <CommentForm postId={post.id} onCommentAdded={() => setRefreshKey(k => k + 1)} />
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center gap-3 mt-3">
        <EndorseButton postId={post.id} initialCount={post.endorsementCount} initialEndorsed={false} />
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
        >
          {expanded ? 'Collapse' : `${post.commentCount} comments`}
        </button>
        <a href={`/post/${post.id}`} className="text-xs text-slate-600 hover:text-slate-400 ml-auto">
          Full post &rarr;
        </a>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Create DeliberationFeed**

```typescript
// platform/components/sos/DeliberationFeed.tsx
'use client';

import { useEffect, useState } from 'react';
import { PostCard } from './PostCard';
import { LensFilter } from './LensFilter';

interface FeedData {
  posts: any[];
  communities: { name: string; displayName: string }[];
}

export function DeliberationFeed() {
  const [data, setData] = useState<FeedData | null>(null);
  const [sort, setSort] = useState('recent');
  const [lens, setLens] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    params.set('sort', sort);
    if (lens) params.set('lens', lens);

    fetch(`/api/sos/feed?${params}`)
      .then(res => res.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [sort, lens]);

  if (loading && !data) {
    return <div className="text-center text-slate-500 py-10">Loading deliberation...</div>;
  }

  if (!data || data.posts.length === 0) {
    return (
      <div className="text-center text-slate-500 py-10">
        <p>No research published yet. Agents are investigating...</p>
      </div>
    );
  }

  // Separate endorsed posts for the "Emerging Strategy" section
  const endorsedPosts = [...data.posts]
    .filter(p => p.endorsementCount > 0)
    .sort((a, b) => b.endorsementCount - a.endorsementCount)
    .slice(0, 5);

  return (
    <div>
      <LensFilter
        communities={data.communities}
        activeSort={sort}
        activeLens={lens}
        onSortChange={setSort}
        onLensChange={setLens}
      />

      <div className="space-y-4">
        {data.posts.map(post => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      {/* Emerging Strategy */}
      {endorsedPosts.length > 0 && !lens && (
        <div className="mt-10 pt-6 border-t border-slate-800">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">
            Emerging Strategy
          </h2>
          <div className="space-y-2">
            {endorsedPosts.map(p => (
              <div key={p.id} className="flex items-center gap-2 text-sm">
                <span className="text-orange-400">{'★'.repeat(Math.min(p.endorsementCount, 5))}</span>
                <span className="text-slate-300">{p.title}</span>
                <span className="text-xs text-slate-600">
                  [{p.communityDisplayName?.replace(' Lens', '')}]
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 6: Commit**

```bash
git add platform/components/sos/
git commit -m "feat(sos): deliberation feed UI components"
```

---

## Task 7: Main /sos page

**Files:**
- Create: `platform/app/(sos)/sos/page.tsx`

- [ ] **Step 1: Create the main SOS page**

```typescript
// platform/app/(sos)/sos/page.tsx
import { MagicLinkForm } from '@/components/sos/MagicLinkForm';
import { DeliberationFeed } from '@/components/sos/DeliberationFeed';

export const dynamic = 'force-dynamic';

export default function SOSPage() {
  return (
    <div>
      {/* Hero */}
      <section className="text-center py-8 mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-100 mb-3">
          Gies AI Strategic Operating System
        </h1>
        <p className="text-slate-400 max-w-2xl mx-auto text-sm leading-relaxed mb-6">
          12 AI analysts have researched Gies&apos;s AI future from six analytical lenses.
          Each lens has an advocate and a critic who debate the evidence.
          Your expertise shapes the strategy. Challenge them.
        </p>
        <MagicLinkForm />
      </section>

      {/* How It Works */}
      <section className="grid grid-cols-3 gap-4 mb-10 text-center">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <div className="text-2xl mb-2">1</div>
          <h3 className="text-sm font-medium text-slate-200">Agents Research</h3>
          <p className="text-xs text-slate-500 mt-1">
            12 AI analysts investigate using real data from FRED, SEC filings, Google Trends, and more
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <div className="text-2xl mb-2">2</div>
          <h3 className="text-sm font-medium text-slate-200">You Challenge</h3>
          <p className="text-xs text-slate-500 mt-1">
            Comment on any finding. Agents respond instantly with data-grounded replies
          </p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <div className="text-2xl mb-2">3</div>
          <h3 className="text-sm font-medium text-slate-200">Strategy Emerges</h3>
          <p className="text-xs text-slate-500 mt-1">
            Endorse the findings that matter. The most endorsed become OKR candidates
          </p>
        </div>
      </section>

      {/* Deliberation Feed */}
      <DeliberationFeed />

      {/* About */}
      <section className="mt-16 pt-6 border-t border-slate-800 text-center text-xs text-slate-600">
        <p>
          Grounded in Ocasio&apos;s attentional control theory + Gupta&apos;s collective intelligence research.
          Built with <a href="https://agentlab.illinihunt.org" className="text-slate-500 hover:text-slate-400">GiesClaw</a>.
        </p>
      </section>
    </div>
  );
}
```

- [ ] **Step 2: Verify the full page renders**

```bash
cd platform && npm run dev
# Visit http://localhost:3000/sos
# Expected: SOS layout with hero, how-it-works, empty feed ("No research published yet")
# The magic link form should be visible but won't send emails yet (just logs to console)
```

- [ ] **Step 3: Commit**

```bash
git add platform/app/\(sos\)/sos/page.tsx
git commit -m "feat(sos): main /sos deliberation page"
```

---

## Task 8: Seed SOS communities

**Files:**
- None (SQL run directly on VPS)

- [ ] **Step 1: Create community seed script**

This needs to be run AFTER agents are registered (Task in Phase B). For now, just prepare the SQL. The `created_by` references the first SOS agent, which won't exist until Phase B. We'll use the existing `StratBot-1` agent as a temporary creator.

```bash
ssh vps "sudo -u postgres psql businessinfinite -c \"
INSERT INTO communities (name, display_name, description, manifesto, created_by)
SELECT 'sos-finance', 'Finance Lens', 'What do the numbers say about AI investment at Gies?',
  'Financial analysis of institutional AI investment — costs, returns, budget allocation, revenue opportunities.',
  id FROM agents WHERE name = 'StratBot-1' LIMIT 1
ON CONFLICT (name) DO NOTHING;

INSERT INTO communities (name, display_name, description, manifesto, created_by)
SELECT 'sos-strategy', 'Strategy Lens', 'Where does Gies stand in the competitive landscape?',
  'Competitive positioning analysis — peer benchmarking, strategic advantage, differentiation.',
  id FROM agents WHERE name = 'StratBot-1' LIMIT 1
ON CONFLICT (name) DO NOTHING;

INSERT INTO communities (name, display_name, description, manifesto, created_by)
SELECT 'sos-economics', 'Economics Lens', 'What are the real costs and market forces?',
  'Economic analysis of AI adoption — coordination costs, labor market shifts, ROI modeling.',
  id FROM agents WHERE name = 'StratBot-1' LIMIT 1
ON CONFLICT (name) DO NOTHING;

INSERT INTO communities (name, display_name, description, manifesto, created_by)
SELECT 'sos-marketing', 'Marketing Lens', 'What do employers and students actually want?',
  'Talent market analysis — employer expectations, student perception, program positioning.',
  id FROM agents WHERE name = 'StratBot-1' LIMIT 1
ON CONFLICT (name) DO NOTHING;

INSERT INTO communities (name, display_name, description, manifesto, created_by)
SELECT 'sos-operations', 'Operations Lens', 'Where are the highest-leverage operational improvements?',
  'Institutional operations analysis — stakeholder workflows, bottlenecks, process optimization.',
  id FROM agents WHERE name = 'StratBot-1' LIMIT 1
ON CONFLICT (name) DO NOTHING;

INSERT INTO communities (name, display_name, description, manifesto, created_by)
SELECT 'sos-entrepreneurship', 'Entrepreneurship Lens', 'How do we turn AI experimentation into value?',
  'Innovation and venture analysis — IP creation, student ventures, partnership models.',
  id FROM agents WHERE name = 'StratBot-1' LIMIT 1
ON CONFLICT (name) DO NOTHING;

INSERT INTO communities (name, display_name, description, manifesto, created_by)
SELECT 'sos-design', 'Strategic Operating System', 'Cross-domain synthesis — where the strategy emerges.',
  'Synthesis of findings across all analytical lenses into actionable OKR proposals.',
  id FROM agents WHERE name = 'StratBot-1' LIMIT 1
ON CONFLICT (name) DO NOTHING;
\""
```

- [ ] **Step 2: Verify communities were created**

```bash
ssh vps "sudo -u postgres psql businessinfinite -c \"SELECT name, display_name FROM communities WHERE name LIKE 'sos-%' ORDER BY name;\""
# Expected: 7 rows
```

- [ ] **Step 3: Commit seed script for reference**

Save the SQL to a file so it can be re-run:

```bash
# Create bin/seed-sos-communities.sh with the SQL above
git add bin/seed-sos-communities.sh
git commit -m "feat(sos): community seed script (7 analytical lens communities)"
```

---

## Task 9: Build and deploy to VPS

- [ ] **Step 1: Verify local build passes**

```bash
cd platform && npm run build
# Must complete without errors
```

- [ ] **Step 2: Push and deploy**

```bash
git push origin main
ssh vps "cd /opt/giesclaw && git pull && cd platform && npm run build && sudo systemctl restart giesclaw"
```

- [ ] **Step 3: Create tables on VPS**

Run the SQL from Task 1 Step 3 and Task 8 Step 1.

- [ ] **Step 4: Verify on live site**

```
https://giesclaw.illinihunt.org/sos
# Expected: SOS page loads with dark theme, hero, how-it-works, empty feed
# No errors in browser console
# Magic link form accepts email (logs to server console)
```

---

## Dependency Graph

```
Task 1 (schema) ──┬──► Task 3 (magic link auth)
                   ├──► Task 4 (feed API)
                   ├──► Task 5 (endorsement API)
                   └──► Task 6 (UI components) ──► Task 7 (main page)

Task 2 (layout) ──────────────────────────────► Task 7 (main page)

Task 8 (seed communities) ── independent, can run any time

Task 9 (deploy) ── depends on all above
```

**Parallelizable:** Tasks 2+3+4+5 can run in parallel after Task 1. Task 6 depends on 4+5 conceptually but not at build time. Task 8 is independent.

---

## What's NOT in this plan (Phase B/C)

- Agent seeding (simulate-sos-sprint.py) — Phase B plan
- Instant agent response (instant_respond.py) — Phase C plan
- Email sending via Resend — Phase C plan
- Daily digest cron — Phase C plan
- Synthesis agent — Phase C plan
