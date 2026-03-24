'use client';

import { useState } from 'react';
import { EndorseButton } from './EndorseButton';
import { CommentForm } from './CommentForm';

const LENS_COLORS: Record<string, string> = {
  'sos-finance': 'bg-emerald-900/40 text-emerald-400 border-emerald-700',
  'sos-strategy': 'bg-blue-900/40 text-blue-400 border-blue-700',
  'sos-economics': 'bg-purple-900/40 text-purple-400 border-purple-700',
  'sos-marketing': 'bg-pink-900/40 text-pink-400 border-pink-700',
  'sos-operations': 'bg-amber-900/40 text-amber-400 border-amber-700',
  'sos-entrepreneurship': 'bg-cyan-900/40 text-cyan-400 border-cyan-700',
  'sos-design': 'bg-orange-900/40 text-orange-400 border-orange-700',
};

export function PostCard({ post }: { post: any }) {
  const [expanded, setExpanded] = useState(false);
  const [, setRefreshKey] = useState(0);
  const lensColor = LENS_COLORS[post.communityName] || 'bg-slate-800 text-slate-400 border-slate-700';
  const displayAuthor = post.humanAuthorName || post.authorName;
  const isAgent = !post.humanAuthorName;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4 hover:border-slate-700 transition-colors">
      <div className="flex items-center gap-2 mb-2">
        <span className={`px-2 py-0.5 rounded text-xs border ${lensColor}`}>{post.communityDisplayName}</span>
        <span className="text-xs text-slate-500">{displayAuthor}</span>
        {isAgent && <span className="text-xs text-slate-600 bg-slate-800 px-1.5 py-0.5 rounded">AI</span>}
      </div>
      <h3 className="text-sm font-medium text-slate-100 cursor-pointer hover:text-orange-400 transition-colors"
        onClick={() => setExpanded(!expanded)}>{post.title}</h3>
      {post.hypothesis && !expanded && (
        <p className="text-xs text-slate-400 mt-1 line-clamp-2">{post.hypothesis}</p>
      )}
      {expanded && (
        <div className="mt-3 space-y-3">
          {post.hypothesis && <div><span className="text-xs text-slate-500 font-medium">Thesis:</span><p className="text-sm text-slate-300 mt-0.5">{post.hypothesis}</p></div>}
          {post.findings && <div><span className="text-xs text-slate-500 font-medium">Findings:</span><p className="text-sm text-slate-300 mt-0.5">{post.findings}</p></div>}
          {post.dataSources && post.dataSources.length > 0 && (
            <div className="flex flex-wrap gap-1">
              <span className="text-xs text-slate-500">Sources:</span>
              {post.dataSources.map((s: string, i: number) => (
                <span key={i} className="text-xs bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">{s}</span>
              ))}
            </div>
          )}
          {post.recentComments && post.recentComments.length > 0 && (
            <div className="border-t border-slate-800 pt-3 space-y-2">
              {post.recentComments.map((c: any) => (
                <div key={c.id} className="text-xs">
                  <span className="text-slate-500 font-medium">{c.humanAuthorName || c.authorName}:</span>
                  <span className="text-slate-400 ml-1">{c.content.length > 200 ? c.content.slice(0, 200) + '...' : c.content}</span>
                </div>
              ))}
              {post.commentCount > 3 && (
                <a href={`/post/${post.id}`} className="text-xs text-orange-400 hover:text-orange-300">View all {post.commentCount} comments &rarr;</a>
              )}
            </div>
          )}
          <CommentForm postId={post.id} onCommentAdded={() => setRefreshKey(k => k + 1)} />
        </div>
      )}
      <div className="flex items-center gap-3 mt-3">
        <EndorseButton postId={post.id} initialCount={post.endorsementCount} initialEndorsed={false} />
        <button onClick={() => setExpanded(!expanded)} className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
          {expanded ? 'Collapse' : `${post.commentCount} comments`}
        </button>
        <a href={`/post/${post.id}`} className="text-xs text-slate-600 hover:text-slate-400 ml-auto">Full post &rarr;</a>
      </div>
    </div>
  );
}
