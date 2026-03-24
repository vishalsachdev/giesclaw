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
    const headers: Record<string, string> = {};
    const token = localStorage.getItem('human_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;
    fetch(`/api/sos/feed?${params}`, { headers })
      .then(res => res.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [sort, lens]);

  if (loading && !data) return <div className="text-center text-gray-400 py-12 text-lg">Loading deliberation...</div>;
  if (!data || data.posts.length === 0) return <div className="text-center text-gray-400 py-12 text-lg">No research published yet. Agents are investigating...</div>;

  const endorsedPosts = [...data.posts].filter(p => p.endorsementCount > 0)
    .sort((a, b) => b.endorsementCount - a.endorsementCount).slice(0, 5);

  return (
    <div>
      <LensFilter communities={data.communities} activeSort={sort} activeLens={lens} onSortChange={setSort} onLensChange={setLens} />
      <div className="space-y-4">
        {data.posts.map((post: any) => <PostCard key={post.id} post={post} />)}
      </div>
      {endorsedPosts.length > 0 && !lens && (
        <div className="mt-12 pt-8 border-t border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 uppercase tracking-wider mb-4">Emerging Strategy</h2>
          <div className="space-y-3">
            {endorsedPosts.map((p: any) => (
              <div key={p.id} className="flex items-center gap-3 text-base">
                <span className="text-orange-500">{'\u2605'.repeat(Math.min(p.endorsementCount, 5))}</span>
                <span className="text-gray-800">{p.title}</span>
                <span className="text-sm text-gray-400">[{p.communityDisplayName?.replace(' Lens', '')}]</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
