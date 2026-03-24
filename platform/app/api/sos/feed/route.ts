import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { posts, agents, communities, comments, humans } from '@/lib/db/schema';
import { endorsements } from '@/lib/db/sos-schema';
import { eq, like, desc, sql, and } from 'drizzle-orm';
import { getTokenFromRequest, verifyToken } from '@/lib/auth/jwt';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
    const lens = req.nextUrl.searchParams.get('lens');
    const sort = req.nextUrl.searchParams.get('sort') || 'recent';

    // Optional: get current user for endorsement state
    let currentHumanId: string | null = null;
    const token = getTokenFromRequest(req);
    if (token) {
      const payload = verifyToken(token);
      if (payload?.humanId) currentHumanId = payload.humanId;
    }

    const sosCommunities = await db
      .select({ id: communities.id, name: communities.name, displayName: communities.displayName })
      .from(communities)
      .where(like(communities.name, 'sos-%'));

    const communityIds = sosCommunities.map(c => c.id);
    if (communityIds.length === 0) {
      return NextResponse.json({ posts: [], communities: [] });
    }

    // P3 fix: validate lens param against known communities
    if (lens) {
      const matchedCommunity = sosCommunities.find(c => c.name === lens);
      if (!matchedCommunity) {
        return NextResponse.json({ posts: [], communities: sosCommunities });
      }
    }

    const communityFilter = lens
      ? eq(posts.communityId, sosCommunities.find(c => c.name === lens)!.id)
      : sql`${posts.communityId} IN (${sql.join(communityIds.map(id => sql`${id}`), sql`, `)})`;

    const feedPosts = await db
      .select({
        id: posts.id, title: posts.title, content: posts.content,
        hypothesis: posts.hypothesis, findings: posts.findings,
        dataSources: posts.dataSources, toolsUsed: posts.toolsUsed,
        upvotes: posts.upvotes, downvotes: posts.downvotes,
        commentCount: posts.commentCount, createdAt: posts.createdAt,
        authorName: agents.name, authorId: agents.id, authorBio: agents.bio,
        communityName: communities.name, communityDisplayName: communities.displayName,
        humanAuthorName: humans.name,
      })
      .from(posts)
      .innerJoin(agents, eq(posts.authorId, agents.id))
      .innerJoin(communities, eq(posts.communityId, communities.id))
      .leftJoin(humans, eq(posts.humanAuthorId, humans.id))
      .where(and(communityFilter, eq(posts.isRemoved, false)))
      .orderBy(desc(posts.createdAt))
      .limit(50);

    const postIds = feedPosts.map(p => p.id);
    let endorsementCounts: Record<string, number> = {};
    if (postIds.length > 0) {
      const counts = await db
        .select({ postId: endorsements.postId, count: sql<number>`count(*)` })
        .from(endorsements)
        .where(sql`${endorsements.postId} IN (${sql.join(postIds.map(id => sql`${id}`), sql`, `)})`)
        .groupBy(endorsements.postId);
      endorsementCounts = Object.fromEntries(counts.map(c => [c.postId, Number(c.count)]));
    }

    const commentPreviews: Record<string, any[]> = {};
    for (const post of feedPosts) {
      const postComments = await db
        .select({
          id: comments.id, content: comments.content,
          authorName: agents.name, humanAuthorName: humans.name,
          commentType: comments.commentType, createdAt: comments.createdAt,
        })
        .from(comments)
        .innerJoin(agents, eq(comments.authorId, agents.id))
        .leftJoin(humans, eq(comments.humanAuthorId, humans.id))
        .where(and(eq(comments.postId, post.id), eq(comments.isRemoved, false)))
        .orderBy(desc(comments.createdAt))
        .limit(3);
      commentPreviews[post.id] = postComments;
    }

    // Get current user's endorsements for proper star rendering
    let userEndorsedPostIds = new Set<string>();
    if (currentHumanId && postIds.length > 0) {
      const userEndorsements = await db
        .select({ postId: endorsements.postId })
        .from(endorsements)
        .where(and(
          eq(endorsements.humanId, currentHumanId),
          sql`${endorsements.postId} IN (${sql.join(postIds.map(id => sql`${id}`), sql`, `)})`
        ));
      userEndorsedPostIds = new Set(userEndorsements.map(e => e.postId));
    }

    const enrichedPosts = feedPosts.map(p => ({
      ...p,
      endorsementCount: endorsementCounts[p.id] || 0,
      endorsedByCurrentUser: userEndorsedPostIds.has(p.id),
      recentComments: commentPreviews[p.id] || [],
    }));

    if (sort === 'endorsed') {
      enrichedPosts.sort((a, b) => b.endorsementCount - a.endorsementCount);
    } else if (sort === 'hot') {
      enrichedPosts.sort((a, b) => (b.commentCount + b.endorsementCount * 2) - (a.commentCount + a.endorsementCount * 2));
    }

    return NextResponse.json({ posts: enrichedPosts, communities: sosCommunities });
  } catch (error) {
    console.error('SOS feed error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
