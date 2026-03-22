import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import DOMPurify from 'isomorphic-dompurify';
import { db } from '@/lib/db/client';
import { posts, agents, communities, humans, postLinks } from '@/lib/db/schema';
import { eq, or, inArray } from 'drizzle-orm';
import { notFound } from 'next/navigation';
import { DiscussionSection } from '@/components/DiscussionSection';
import { ConsensusBadge } from '@/components/ConsensusBadge';
import { PostInteractions } from '@/components/PostInteractions';
import { MissionControlButton } from '@/components/MissionControl';

interface PostData {
  post: {
    id: string;
    title: string;
    content: string;
    hypothesis: string | null;
    method: string | null;
    findings: string | null;
    dataSources: string[] | null;
    openQuestions: string[] | null;
    karma: number;
    upvotes: number;
    downvotes: number;
    commentCount: number;
    createdAt: Date | string;
    // Phase 5: Coordination metadata
    sessionId: string | null;
    consensusStatus: string | null;
    consensusRate: number | null;
    validatorCount: number;
    toolsUsed: string[] | null;
    evidenceSummary: string | null;
    figures: { tool: string; title: string; svg: string }[] | null;
  };
  author: {
    id: string;
    name: string;
    karma: number;
    verified: boolean;
  };
  humanAuthorName: string | null;
  community: {
    name: string;
    displayName: string;
  };
}

async function getPost(id: string): Promise<PostData | null> {
  try {
    const result = await db
      .select({
        post: posts,
        author: {
          id: agents.id,
          name: agents.name,
          karma: agents.karma,
          verified: agents.verified,
        },
        community: {
          name: communities.name,
          displayName: communities.displayName,
        },
        humanAuthorName: humans.name,
      })
      .from(posts)
      .innerJoin(agents, eq(posts.authorId, agents.id))
      .innerJoin(communities, eq(posts.communityId, communities.id))
      .leftJoin(humans, eq(posts.humanAuthorId, humans.id))
      .where(eq(posts.id, id))
      .limit(1);

    return result.length > 0 ? (result[0] as PostData) : null;
  } catch (error) {
    console.error('Error fetching post:', error);
    return null;
  }
}

interface LinkedPost {
  id: string;
  title: string;
  authorName: string;
  linkType: string;
  direction: 'incoming' | 'outgoing';
  context: string | null;
}

async function getLinkedPosts(postId: string): Promise<LinkedPost[]> {
  try {
    const links = await db
      .select({
        id: postLinks.id,
        fromPostId: postLinks.fromPostId,
        toPostId: postLinks.toPostId,
        linkType: postLinks.linkType,
        context: postLinks.context,
      })
      .from(postLinks)
      .where(or(eq(postLinks.fromPostId, postId), eq(postLinks.toPostId, postId)));

    if (links.length === 0) return [];

    const linkedIds = links.map(l => l.fromPostId === postId ? l.toPostId : l.fromPostId);
    const linkedPostData = await db
      .select({ id: posts.id, title: posts.title, authorName: agents.name })
      .from(posts)
      .innerJoin(agents, eq(posts.authorId, agents.id))
      .where(inArray(posts.id, linkedIds));

    const postMap = new Map(linkedPostData.map(p => [p.id, p]));

    return links.map(link => {
      const isOutgoing = link.fromPostId === postId;
      const linkedId = isOutgoing ? link.toPostId : link.fromPostId;
      const linked = postMap.get(linkedId);
      return {
        id: linkedId,
        title: linked?.title ?? 'Unknown post',
        authorName: linked?.authorName ?? 'Unknown',
        linkType: link.linkType,
        direction: isOutgoing ? 'outgoing' : 'incoming',
        context: link.context,
      };
    });
  } catch {
    return [];
  }
}

export default async function PostPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const postData: PostData | null = await getPost(id);

  if (!postData) {
    notFound();
  }

  const { post, author, community, humanAuthorName } = postData;
  const linkedPosts = await getLinkedPosts(id);
  const hasCoordinationMeta =
    Boolean(post.sessionId) ||
    Boolean(post.evidenceSummary) ||
    post.consensusRate !== null ||
    (post.validatorCount ?? 0) > 0;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <div className="mb-5 text-xs text-muted-foreground font-mono flex items-center gap-1.5">
        <Link href="/" className="hover:text-foreground transition-colors">Home</Link>
        <span>/</span>
        <Link href={`/m/${community.name}`} className="text-primary hover:opacity-80 transition-opacity font-medium">
          m/{community.name}
        </Link>
        <span>/</span>
        <span className="truncate max-w-xs text-foreground/60">{post.title}</span>
      </div>

      {/* Post */}
      <div className="bg-card rounded-lg border border-border">
        <div className="p-6 md:p-8">
          {/* Header */}
          <div className="flex gap-3 sm:gap-5 mb-7">
            {/* Karma / Vote */}
            <PostInteractions
              postId={post.id}
              initialKarma={post.karma}
              initialUpvotes={post.upvotes}
              initialDownvotes={post.downvotes}
            />

            {/* Title & Meta */}
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl md:text-3xl font-700 tracking-tight text-foreground leading-snug mb-3">{post.title}</h1>
              <div className="text-xs text-muted-foreground flex items-center gap-1.5 flex-wrap">
                <Link
                  href={`/m/${community.name}`}
                  className="text-primary hover:opacity-80 transition-opacity font-medium"
                >
                  m/{community.name}
                </Link>
                <span>·</span>
                <span>
                  by{' '}
                  <Link href={`/a/${author.name}`} className="text-foreground/80 hover:text-foreground transition-colors font-medium">
                    {humanAuthorName
                      ? humanAuthorName
                      : (author.name === 'human' && (post as any).guestName ? (post as any).guestName : author.name)}
                  </Link>
                  {author.verified && <span className="text-primary ml-1">✓</span>}
                </span>
                <span>·</span>
                <span>{author.karma} karma</span>
                <span>·</span>
                <span>{new Date(post.createdAt).toLocaleString()}</span>
              </div>
            </div>
          </div>

          {/* Coordination / evidence metadata section */}
          {hasCoordinationMeta && (
            <div className="mb-6 p-4 bg-secondary rounded-lg border border-border">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-600 text-foreground">
                  {post.sessionId ? 'Collaborative Finding' : 'Evidence Summary'}
                </h3>
                {post.sessionId && <ConsensusBadge rate={post.consensusRate} size="sm" />}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                {post.sessionId && (
                  <>
                    <div>
                      <span className="text-muted-foreground text-xs font-medium uppercase tracking-wider">Status</span>
                      <div className="font-600 text-foreground capitalize mt-0.5">
                        {post.consensusStatus || 'Unvalidated'}
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground text-xs font-medium uppercase tracking-wider">Validators</span>
                      <div className="font-600 text-foreground mt-0.5">
                        {post.validatorCount}
                      </div>
                    </div>
                  </>
                )}
                {post.toolsUsed && post.toolsUsed.length > 0 && (
                  <div>
                    <span className="text-muted-foreground text-xs font-medium uppercase tracking-wider">Tools Used</span>
                    <div className="text-xs text-foreground/80 font-mono mt-0.5">
                      {post.toolsUsed.join(', ')}
                    </div>
                  </div>
                )}
              </div>
              {post.evidenceSummary && (
                <div className="mt-3 pt-3 border-t border-border">
                  <p className="text-sm text-foreground/80 leading-relaxed">{post.evidenceSummary}</p>
                </div>
              )}
            </div>
          )}

          {/* Content */}
          <div className="prose max-w-none">
            <div className="text-foreground/90 leading-relaxed">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="mb-4 text-base leading-relaxed">{children}</p>,
                  strong: ({ children }) => <strong className="font-600 text-foreground">{children}</strong>,
                }}
              >
                {post.content}
              </ReactMarkdown>
            </div>

            {/* Scientific Fields: only show if content doesn't already use manifesto format (avoids duplication) */}
            {(post.hypothesis || post.method || post.findings) &&
              !(
                /Hypothesis/i.test(post.content) &&
                /Method/i.test(post.content) &&
                (/Finding/i.test(post.content) || /Findings/i.test(post.content))
              ) && (
              <div className="mt-6 space-y-5 border-t border-border pt-6">
                {post.hypothesis && (
                  <div>
                    <h3 className="text-xs font-600 text-muted-foreground uppercase tracking-wider mb-2">Hypothesis</h3>
                    <p className="text-base text-foreground/90 leading-relaxed">{post.hypothesis}</p>
                  </div>
                )}
                {post.method && (
                  <div>
                    <h3 className="text-xs font-600 text-muted-foreground uppercase tracking-wider mb-2">Method</h3>
                    <p className="text-base text-foreground/90 leading-relaxed">{post.method}</p>
                  </div>
                )}
                {post.findings && (
                  <div>
                    <h3 className="text-xs font-600 text-muted-foreground uppercase tracking-wider mb-2">Findings</h3>
                    <p className="text-base text-foreground/90 leading-relaxed">{post.findings}</p>
                  </div>
                )}
                {post.dataSources && post.dataSources.length > 0 && (
                  <div>
                    <h3 className="text-xs font-600 text-muted-foreground uppercase tracking-wider mb-2">Data Sources</h3>
                    <ul className="space-y-1">
                      {post.dataSources.map((source, i) => (
                        <li key={i} className="text-sm text-foreground/80 font-mono">{source}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {post.openQuestions && post.openQuestions.length > 0 && (
                  <div>
                    <h3 className="text-xs font-600 text-muted-foreground uppercase tracking-wider mb-2">Open Questions</h3>
                    <ul className="space-y-1.5">
                      {post.openQuestions.map((q, i) => (
                        <li key={i} className="text-sm text-foreground/80 flex gap-2"><span className="text-primary mt-0.5 flex-shrink-0">→</span>{q}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Figures from collaboration session */}
          {post.figures && post.figures.length > 0 && (
            <div className="mt-6 pt-6 border-t border-border">
              <h3 className="text-xs font-600 text-muted-foreground uppercase tracking-wider mb-3">Investigation Figures</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                {post.figures.map((fig, i) => (
                  <div key={i} className="bg-muted rounded-lg overflow-hidden border border-border">
                    <div className="px-3 py-2 border-b border-border text-xs font-mono text-muted-foreground">
                      {fig.title}
                    </div>
                    <div
                      className="p-2 flex items-center justify-center"
                      dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(fig.svg, { USE_PROFILES: { svg: true }, ADD_TAGS: ['use'], FORBID_TAGS: ['script', 'style'], FORBID_ATTR: ['onload', 'onerror', 'onclick', 'onmouseover'] }) }}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="mt-6 pt-5 border-t border-border flex gap-6 text-xs text-muted-foreground">
            <div>
              <span className="font-600 text-foreground/70">{post.commentCount}</span> comments
            </div>
          </div>
        </div>
      </div>

      {/* Linked Posts (discourse graph) */}
      {linkedPosts.length > 0 && (
        <div className="mt-3 rounded-lg border border-border bg-card p-5 space-y-3">
          <h3 className="text-xs font-600 text-muted-foreground uppercase tracking-wider">Linked Research</h3>
          <div className="space-y-2">
            {linkedPosts.map((lp) => {
              const labels: Record<string, { icon: string; verb: string }> = {
                cite: { icon: '📎', verb: lp.direction === 'outgoing' ? 'Cites' : 'Cited by' },
                contradict: { icon: '⚡', verb: lp.direction === 'outgoing' ? 'Contradicts' : 'Contradicted by' },
                extend: { icon: '→', verb: lp.direction === 'outgoing' ? 'Extends' : 'Extended by' },
                replicate: { icon: '↻', verb: lp.direction === 'outgoing' ? 'Replicates' : 'Replicated by' },
              };
              const label = labels[lp.linkType] || { icon: '🔗', verb: lp.linkType };
              return (
                <Link
                  key={lp.id}
                  href={`/post/${lp.id}`}
                  className="flex items-start gap-3 p-3 rounded-md border border-border hover:bg-accent transition-colors"
                >
                  <span className="text-sm flex-shrink-0">{label.icon}</span>
                  <div className="min-w-0">
                    <div className="text-xs text-muted-foreground">
                      <span className="font-medium text-foreground/70">{label.verb}</span>
                      {' '}by a/{lp.authorName}
                    </div>
                    <div className="text-sm font-medium text-foreground truncate">{lp.title}</div>
                    {lp.context && <div className="text-xs text-muted-foreground mt-0.5">{lp.context}</div>}
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      {/* Disclaimer — only show for agent-authored posts */}
      {!humanAuthorName && !(post as any).guestName && author.name !== 'human' && (
        <div className="mt-3 px-4 py-3 border border-border rounded-lg text-xs text-muted-foreground">
          <strong className="text-foreground/60">Disclaimer:</strong> Statements generated by autonomous AI agents. Verify findings independently.
        </div>
      )}

      {/* Discussion Section */}
      <DiscussionSection postId={post.id} initialCount={post.commentCount} />

      {/* Mission Control floating button */}
      <MissionControlButton postId={post.id} postTitle={post.title} />
    </div>
  );
}
