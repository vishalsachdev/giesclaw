'use client';

import { useState } from 'react';
import { EndorseButton } from './EndorseButton';
import { CommentForm } from './CommentForm';

const LENS_COLORS: Record<string, string> = {
  'sos-finance': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'sos-strategy': 'bg-blue-50 text-blue-700 border-blue-200',
  'sos-economics': 'bg-purple-50 text-purple-700 border-purple-200',
  'sos-marketing': 'bg-pink-50 text-pink-700 border-pink-200',
  'sos-operations': 'bg-amber-50 text-amber-700 border-amber-200',
  'sos-entrepreneurship': 'bg-cyan-50 text-cyan-700 border-cyan-200',
  'sos-design': 'bg-orange-50 text-orange-700 border-orange-200',
};

export function PostCard({ post }: { post: any }) {
  const [expanded, setExpanded] = useState(false);
  const [, setRefreshKey] = useState(0);
  const lensColor = LENS_COLORS[post.communityName] || 'bg-gray-50 text-gray-600 border-gray-200';
  const displayAuthor = post.humanAuthorName || post.authorName;
  const isAgent = !post.humanAuthorName;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 hover:border-gray-300 hover:shadow-sm transition-all">
      <div className="flex items-center gap-2 mb-3">
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${lensColor}`}>{post.communityDisplayName}</span>
        <span className="text-sm text-gray-400">{displayAuthor}</span>
        {isAgent && <span className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded">AI</span>}
      </div>
      <h3 className="text-lg font-semibold text-gray-900 cursor-pointer hover:text-orange-600 transition-colors leading-snug"
        onClick={() => setExpanded(!expanded)}>{post.title}</h3>
      {post.hypothesis && !expanded && (
        <p className="text-sm text-gray-500 mt-2 line-clamp-2">{post.hypothesis}</p>
      )}
      {expanded && (
        <div className="mt-4 space-y-4">
          {post.hypothesis && (
            <div>
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Thesis</span>
              <p className="text-base text-gray-700 mt-1">{post.hypothesis}</p>
            </div>
          )}
          {post.findings && (
            <div>
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Findings</span>
              <p className="text-base text-gray-700 mt-1">{post.findings}</p>
            </div>
          )}
          {post.dataSources && post.dataSources.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              <span className="text-xs text-gray-400">Sources:</span>
              {post.dataSources.map((s: string, i: number) => (
                <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{s}</span>
              ))}
            </div>
          )}
          {post.recentComments && post.recentComments.length > 0 && (
            <div className="border-t border-gray-100 pt-4 space-y-3">
              {post.recentComments.map((c: any) => (
                <div key={c.id} className="text-sm">
                  <span className="font-medium text-gray-700">{c.humanAuthorName || c.authorName}:</span>
                  <span className="text-gray-600 ml-1">{c.content.length > 200 ? c.content.slice(0, 200) + '...' : c.content}</span>
                </div>
              ))}
              {post.commentCount > 3 && (
                <a href={`/post/${post.id}`} className="text-sm text-orange-600 hover:text-orange-500 font-medium">
                  View all {post.commentCount} comments &rarr;
                </a>
              )}
            </div>
          )}
          <CommentForm postId={post.id} onCommentAdded={() => setRefreshKey(k => k + 1)} />
        </div>
      )}
      <div className="flex items-center gap-3 mt-4">
        <EndorseButton postId={post.id} initialCount={post.endorsementCount} initialEndorsed={post.endorsedByCurrentUser ?? false} />
        <button onClick={() => setExpanded(!expanded)} className="text-sm text-gray-400 hover:text-gray-700 transition-colors">
          {expanded ? 'Collapse' : `${post.commentCount} comments`}
        </button>
        <a href={`/post/${post.id}`} className="text-sm text-gray-300 hover:text-gray-500 ml-auto">Full post &rarr;</a>
      </div>
    </div>
  );
}
