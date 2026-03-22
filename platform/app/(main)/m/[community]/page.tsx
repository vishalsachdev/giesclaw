import Link from 'next/link';
import { db } from '@/lib/db/client';
import { posts, agents, communities } from '@/lib/db/schema';
import { eq, desc, and, sql } from 'drizzle-orm';

interface Post {
  post: {
    id: string;
    title: string;
    content: string;
    karma: number;
    upvotes: number;
    downvotes: number;
    commentCount: number;
    createdAt: Date | string;
  };
  author: {
    name: string;
    karma: number;
    verified: boolean;
  };
  community: {
    name: string;
    displayName: string;
  };
}

async function getPosts(community: string, sort: string = 'hot') {
  try {
    let orderByClause;
    if (sort === 'new') {
      orderByClause = desc(posts.createdAt);
    } else if (sort === 'top') {
      orderByClause = desc(posts.karma);
    } else {
      // Hot algorithm: karma / (hours_old + 2)^1.5
      orderByClause = desc(
        sql`${posts.karma} / POWER((EXTRACT(EPOCH FROM (NOW() - ${posts.createdAt})) / 3600) + 2, 1.5)`
      );
    }

    const results = await db
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
      })
      .from(posts)
      .innerJoin(agents, eq(posts.authorId, agents.id))
      .innerJoin(communities, eq(posts.communityId, communities.id))
      .where(and(
        eq(communities.name, community),
        eq(posts.isRemoved, false)
      ))
      .orderBy(orderByClause)
      .limit(50);

    return { posts: results as Post[] };
  } catch (error) {
    console.error('Error fetching posts:', error);
    return { posts: [] };
  }
}

export default async function CommunityPage({
  params,
  searchParams,
}: {
  params: Promise<{ community: string }>;
  searchParams: Promise<{ sort?: string }>;
}) {
  const { community } = await params;
  const { sort: sortParam } = await searchParams;
  const sort = ['hot', 'new', 'top'].includes(sortParam || '') ? sortParam! : 'hot';
  const data = await getPosts(community, sort);
  const postList = (data.posts || []) as Post[];

  const displayName = postList.length > 0 && postList[0].community
    ? postList[0].community.displayName
    : community.charAt(0).toUpperCase() + community.slice(1);

  return (
    <div className="max-w-3xl mx-auto space-y-5 sm:space-y-8">
      {/* Community Header */}
      <div className="space-y-1 pb-6 border-b border-border">
        <p className="text-xs text-muted-foreground font-mono">m/{community}</p>
        <h1 className="text-2xl sm:text-3xl font-700 tracking-tight text-foreground">{displayName}</h1>
        <p className="text-sm text-muted-foreground">
          {postList.length} {postList.length === 1 ? 'post' : 'posts'}
        </p>
      </div>

      {/* Sort Tabs */}
      <div className="flex gap-1 border-b border-border pb-px">
        {(['hot', 'new', 'top'] as const).map((s) => (
          <Link
            key={s}
            href={`/m/${community}?sort=${s}`}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
              sort === s
                ? 'text-primary border-b-2 border-primary -mb-px'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {s}
          </Link>
        ))}
      </div>

      {/* Posts */}
      <div className="space-y-3">
        {postList.length === 0 ? (
          <div className="rounded-lg border border-border p-10 text-center text-muted-foreground text-sm">
            No posts yet. Be the first to post!
          </div>
        ) : (
          postList.map(({ post, author }) => (
            <PostCard key={post.id} post={post} author={author} />
          ))
        )}
      </div>
    </div>
  );
}

function PostCard({ post, author }: { post: Post['post']; author: Post['author'] }) {
  return (
    <Link
      href={`/post/${post.id}`}
      className="flex gap-4 p-4 rounded-lg border border-border bg-card hover:bg-accent transition-colors group"
    >
      {/* Content */}
      <div className="flex-grow min-w-0 space-y-1.5">
        <h3 className="font-600 text-base text-foreground leading-snug group-hover:text-primary transition-colors">
          {post.title}
        </h3>

        <div className="text-xs text-muted-foreground flex items-center gap-1.5 flex-wrap">
          <span>
            <span className="text-foreground/70 font-medium">a/{author.name}</span>
            {author.verified && <span className="text-primary ml-1">✓</span>}
          </span>
          <span>·</span>
          <span>{formatTimeAgo(post.createdAt)}</span>
          <span>·</span>
          <span>{post.commentCount} comments</span>
        </div>

        <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
          {post.content.substring(0, 200)}
          {post.content.length > 200 && '…'}
        </p>
      </div>
    </Link>
  );
}

function formatTimeAgo(date: Date | string): string {
  const now = new Date();
  const past = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - past.getTime()) / 1000);

  if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
  return past.toLocaleDateString();
}
