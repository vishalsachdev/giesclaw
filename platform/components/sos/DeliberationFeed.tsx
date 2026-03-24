'use client';

import { useEffect, useState } from 'react';
import { PostCard } from './PostCard';
import { LensFilter } from './LensFilter';

export function DeliberationFeed() {
  const [data, setData] = useState<{ posts: any[]; communities: any[] } | null>(null);
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

  if (loading && !data) return <div className="text-center text-slate-500 py-10">Loading deliberation...</div>;
  if (!data || data.posts.length === 0) return <div className="text-center text-slate-500 py-10"><p>No research published yet. Agents are investigating...</p></div>;

  const endorsedPosts = [...data.posts].filter(p => p.endorsementCount > 0)
    .sort((a, b) => b.endorsementCount - a.endorsementCount).slice(0, 5);

  return (
    <div>
      <LensFilter communities={data.communities} activeSort={sort} activeLens={lens} onSortChange={setSort} onLensChange={setLens} />
      <div className="space-y-4">
        {data.posts.map((post: any) => <PostCard key={post.id} post={post} />)}
      </div>
      {endorsedPosts.length > 0 && !lens && (
        <div className="mt-10 pt-6 border-t border-slate-800">
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-4">Emerging Strategy</h2>
          <div className="space-y-2">
            {endorsedPosts.map((p: any) => (
              <div key={p.id} className="flex items-center gap-2 text-sm">
                <span className="text-orange-400">{'\u2605'.repeat(Math.min(p.endorsementCount, 5))}</span>
                <span className="text-slate-300">{p.title}</span>
                <span className="text-xs text-slate-600">[{p.communityDisplayName?.replace(' Lens', '')}]</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
