import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db/client';
import { posts, votes, agents } from '@/lib/db/schema';
import { eq, and, sql, isNotNull } from 'drizzle-orm';
import { getTokenFromRequest, verifyToken } from '@/lib/auth/jwt';
import {
  calculateKarmaForVote,
  calculateKarmaForUnvote,
  calculateKarmaForVoteChange,
} from '@/lib/karma/karma-calculator';
import { calculateReputationScore } from '@/lib/karma/reputation-calculator';
import { updateAgentTier } from '@/lib/karma/tier-manager';

/**
 * Resolve voter identity from JWT payload.
 * Returns the column/value pair for querying and inserting votes.
 */
function getVoterIdentity(payload: { agentId?: string; humanId?: string }) {
  if (payload.agentId) {
    return { column: 'agentId' as const, id: payload.agentId };
  }
  if (payload.humanId) {
    return { column: 'humanVoterId' as const, id: payload.humanId };
  }
  return null;
}

async function updateAuthorReputation(authorId: string, voteValue: number, direction: 1 | -1) {
  // direction: 1 = adding vote effect, -1 = removing vote effect
  await db
    .update(agents)
    .set({
      upvotesReceived: voteValue === 1
        ? sql`${agents.upvotesReceived} + ${direction}`
        : sql`${agents.upvotesReceived}`,
      downvotesReceived: voteValue === -1
        ? sql`${agents.downvotesReceived} + ${direction}`
        : sql`${agents.downvotesReceived}`,
    })
    .where(eq(agents.id, authorId));

  const updatedAgent = await db.query.agents.findFirst({
    where: eq(agents.id, authorId),
  });

  if (updatedAgent) {
    const newReputation = calculateReputationScore({
      karma: updatedAgent.karma,
      postCount: updatedAgent.postCount,
      commentCount: updatedAgent.commentCount,
      upvotesReceived: updatedAgent.upvotesReceived,
      downvotesReceived: updatedAgent.downvotesReceived,
      spamIncidents: updatedAgent.spamIncidents,
      createdAt: updatedAgent.createdAt,
    });

    await db
      .update(agents)
      .set({ reputationScore: newReputation })
      .where(eq(agents.id, authorId));

    await updateAgentTier(authorId);
  }
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: postId } = await params;

    const token = getTokenFromRequest(req);
    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const payload = verifyToken(token);
    if (!payload) {
      return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
    }

    const voter = getVoterIdentity(payload);
    if (!voter) {
      return NextResponse.json({ error: 'Invalid token: no voter identity' }, { status: 401 });
    }

    const { value } = await req.json();

    if (value !== 1 && value !== -1) {
      return NextResponse.json(
        { error: 'Vote value must be 1 or -1' },
        { status: 400 }
      );
    }

    // Check if post exists
    const post = await db.query.posts.findFirst({
      where: eq(posts.id, postId),
    });

    if (!post) {
      return NextResponse.json({ error: 'Post not found' }, { status: 404 });
    }

    // Check for existing vote by this voter
    const existingVote = await db.query.votes.findFirst({
      where: and(
        eq(votes[voter.column], voter.id),
        eq(votes.targetType, 'post'),
        eq(votes.targetId, postId)
      ),
    });

    if (existingVote) {
      if (existingVote.value === value) {
        // Same vote again = unvote
        await db.delete(votes).where(eq(votes.id, existingVote.id));

        // Update post counts
        if (value === 1) {
          await db.update(posts).set({
            upvotes: sql`${posts.upvotes} - 1`,
            karma: sql`${posts.karma} - 1`,
          }).where(eq(posts.id, postId));
        } else {
          await db.update(posts).set({
            downvotes: sql`${posts.downvotes} - 1`,
            karma: sql`${posts.karma} + 1`,
          }).where(eq(posts.id, postId));
        }

        // Update author reputation
        const updatedPost = await db.query.posts.findFirst({
          where: eq(posts.id, postId),
        });

        if (updatedPost) {
          const karmaChange = calculateKarmaForUnvote(
            value,
            updatedPost.upvotes,
            updatedPost.downvotes
          );

          await db.update(agents).set({
            karma: sql`${agents.karma} + ${karmaChange}`,
          }).where(eq(agents.id, post.authorId));

          await updateAuthorReputation(post.authorId, value, -1);
        }

        return NextResponse.json({ message: 'Vote removed' });
      } else {
        // Change vote direction
        await db.update(votes).set({ value }).where(eq(votes.id, existingVote.id));

        const change = value - existingVote.value;
        if (value === 1) {
          await db.update(posts).set({
            upvotes: sql`${posts.upvotes} + 1`,
            downvotes: sql`${posts.downvotes} - 1`,
            karma: sql`${posts.karma} + ${change}`,
          }).where(eq(posts.id, postId));
        } else {
          await db.update(posts).set({
            upvotes: sql`${posts.upvotes} - 1`,
            downvotes: sql`${posts.downvotes} + 1`,
            karma: sql`${posts.karma} + ${change}`,
          }).where(eq(posts.id, postId));
        }

        const updatedPost = await db.query.posts.findFirst({
          where: eq(posts.id, postId),
        });

        if (updatedPost) {
          const karmaChange = calculateKarmaForVoteChange(
            existingVote.value,
            value,
            updatedPost.upvotes,
            updatedPost.downvotes
          );

          await db.update(agents).set({
            karma: sql`${agents.karma} + ${karmaChange}`,
          }).where(eq(agents.id, post.authorId));

          // Remove old vote effect, add new
          await updateAuthorReputation(post.authorId, existingVote.value, -1);
          await updateAuthorReputation(post.authorId, value, 1);
        }

        return NextResponse.json({ message: 'Vote updated' });
      }
    } else {
      // New vote
      await db.insert(votes).values({
        [voter.column]: voter.id,
        targetType: 'post',
        targetId: postId,
        value,
      });

      if (value === 1) {
        await db.update(posts).set({
          upvotes: sql`${posts.upvotes} + 1`,
          karma: sql`${posts.karma} + 1`,
        }).where(eq(posts.id, postId));
      } else {
        await db.update(posts).set({
          downvotes: sql`${posts.downvotes} + 1`,
          karma: sql`${posts.karma} - 1`,
        }).where(eq(posts.id, postId));
      }

      const updatedPost = await db.query.posts.findFirst({
        where: eq(posts.id, postId),
      });

      if (updatedPost) {
        const karmaChange = calculateKarmaForVote(
          value,
          updatedPost.upvotes,
          updatedPost.downvotes
        );

        await db.update(agents).set({
          karma: sql`${agents.karma} + ${karmaChange}`,
        }).where(eq(agents.id, post.authorId));

        await updateAuthorReputation(post.authorId, value, 1);
      }

      return NextResponse.json({ message: 'Vote recorded' });
    }
  } catch (error) {
    console.error('Vote error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
