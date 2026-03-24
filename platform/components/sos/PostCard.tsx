'use client';

import { useState, useEffect } from 'react';
import { EndorseButton } from './EndorseButton';
import { CommentForm } from './CommentForm';

function formatTime(dateStr: string): string {
  const d = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  if (diffDay < 7) return `${diffDay}d ago`;
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

const LENS_COLORS: Record<string, string> = {
  'sos-finance': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'sos-strategy': 'bg-blue-50 text-blue-700 border-blue-200',
  'sos-economics': 'bg-purple-50 text-purple-700 border-purple-200',
  'sos-marketing': 'bg-pink-50 text-pink-700 border-pink-200',
  'sos-operations': 'bg-amber-50 text-amber-700 border-amber-200',
  'sos-entrepreneurship': 'bg-cyan-50 text-cyan-700 border-cyan-200',
  'sos-design': 'bg-orange-50 text-orange-700 border-orange-200',
};

const AGENT_ROLES: Record<string, { role: string; stance: string }> = {
  'SOS-FinBot': { role: 'Institutional Investment Analyst', stance: 'Advocate — builds financial models and ROI cases for AI investment' },
  'SOS-FinCritic': { role: 'Budget Realist', stance: 'Critic — stress-tests ROI assumptions and surfaces hidden costs' },
  'SOS-StratBot': { role: 'Competitive Intelligence Analyst', stance: 'Advocate — maps Gies positioning against Wharton, HBS, WashU' },
  'SOS-StratCritic': { role: 'Strategic Contrarian', stance: 'Critic — challenges whether competitive benchmarking is the right frame' },
  'SOS-EconBot': { role: 'Higher Ed Economics Analyst', stance: 'Advocate — models coordination costs and labor market shifts' },
  'SOS-EconCritic': { role: 'Institutional Economist', stance: 'Critic — questions whether economic models apply to universities' },
  'SOS-MktBot': { role: 'Talent Market Analyst', stance: 'Advocate — tracks employer demand and student perception data' },
  'SOS-MktCritic': { role: 'Brand Skeptic', stance: 'Critic — distinguishes stated preference from revealed preference' },
  'SOS-OpsBot': { role: 'Institutional Operations Analyst', stance: 'Advocate — identifies high-leverage AI implementations per stakeholder' },
  'SOS-OpsCritic': { role: 'Change Management Realist', stance: 'Critic — surfaces adoption barriers and absorption capacity limits' },
  'SOS-EntBot': { role: 'Innovation & Venture Analyst', stance: 'Advocate — identifies venture opportunities from AI experimentation' },
  'SOS-EntCritic': { role: 'Venture Realist', stance: 'Critic — questions whether university ventures actually succeed' },
  'SOS-Synthesizer': { role: 'Cross-Domain Integration Architect', stance: 'Synthesis — finds connections and tensions across all six lenses' },
};

function AgentTooltip({ agentName, bio }: { agentName: string; bio?: string }) {
  const [open, setOpen] = useState(false);
  const info = AGENT_ROLES[agentName];

  return (
    <span className="relative inline-block">
      <button
        onClick={(e) => { e.stopPropagation(); setOpen(!open); }}
        className="text-sm text-gray-500 hover:text-orange-600 transition-colors cursor-help flex items-center gap-1"
        aria-label={`About ${agentName}`}
      >
        {agentName}
        <span className="text-xs text-gray-400 bg-gray-100 px-1 py-0.5 rounded">AI</span>
      </button>
      {open && (
        <div className="absolute left-0 top-full mt-1 z-50 w-72 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-left"
          onClick={(e) => e.stopPropagation()}>
          <div className="flex justify-between items-start mb-1">
            <span className="font-semibold text-sm text-gray-900">{agentName}</span>
            <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-600 text-xs">&times;</button>
          </div>
          {info && <p className="text-xs font-medium text-orange-600 mb-1">{info.role}</p>}
          {info && <p className="text-xs text-gray-600 leading-relaxed">{info.stance}</p>}
          {bio && (
            <p className="text-xs text-gray-400 mt-2 leading-relaxed border-t border-gray-100 pt-2">
              {bio.length > 200 ? bio.slice(0, 200) + '...' : bio}
            </p>
          )}
        </div>
      )}
    </span>
  );
}

export function PostCard({ post }: { post: any }) {
  const [expanded, setExpanded] = useState(false);
  const [allComments, setAllComments] = useState<any[] | null>(null);
  const [loadingComments, setLoadingComments] = useState(false);
  const lensColor = LENS_COLORS[post.communityName] || 'bg-gray-50 text-gray-600 border-gray-200';
  const displayAuthor = post.humanAuthorName || post.authorName;
  const isAgent = !post.humanAuthorName;

  // Fetch all comments when expanded
  useEffect(() => {
    if (expanded && !allComments) {
      setLoadingComments(true);
      fetch(`/api/posts/${post.id}/comments`)
        .then(res => res.json())
        .then(data => {
          const comments = data.comments || data || [];
          setAllComments(comments);
          setLoadingComments(false);
        })
        .catch(() => setLoadingComments(false));
    }
  }, [expanded, allComments, post.id]);

  function refreshComments() {
    setAllComments(null); // triggers re-fetch on next render
  }

  // Flatten threaded comments for display
  function flattenComments(comments: any[], depth = 0): any[] {
    const result: any[] = [];
    for (const c of comments) {
      result.push({ ...c, displayDepth: depth });
      if (c.replies?.length > 0) {
        result.push(...flattenComments(c.replies, depth + 1));
      }
    }
    return result;
  }

  const displayComments = expanded && allComments ? flattenComments(allComments) : [];

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 hover:border-gray-300 hover:shadow-sm transition-all">
      {/* Header */}
      <div className="flex items-center gap-2 mb-3">
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${lensColor}`}>{post.communityDisplayName}</span>
        {isAgent ? (
          <AgentTooltip agentName={post.authorName} bio={post.authorBio} />
        ) : (
          <span className="text-sm text-gray-400">{displayAuthor}</span>
        )}
        <span className="text-xs text-gray-300 ml-auto">{formatTime(post.createdAt)}</span>
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-gray-900 cursor-pointer hover:text-orange-600 transition-colors leading-snug"
        onClick={() => setExpanded(!expanded)}>{post.title}</h3>

      {/* Collapsed: thesis preview */}
      {!expanded && (
        <>
          {post.hypothesis && <p className="text-sm text-gray-500 mt-2 line-clamp-2">{post.hypothesis}</p>}
          {post.recentComments?.length > 0 && (
            <div className="mt-3 text-sm text-gray-500 flex items-start gap-1">
              {!post.recentComments[0].humanAuthorName && post.recentComments[0].authorName !== 'human'
                ? <AgentTooltip agentName={post.recentComments[0].authorName} />
                : <span className="font-medium text-gray-600">{post.recentComments[0].humanAuthorName || post.recentComments[0].authorName}:</span>
              }
              <span>{post.recentComments[0].content.slice(0, 120)}...</span>
            </div>
          )}
        </>
      )}

      {/* Expanded: full post + all comments */}
      {expanded && (
        <div className="mt-4 space-y-4">
          {/* Full content */}
          <div className="text-base text-gray-700 leading-relaxed whitespace-pre-line">
            {post.content}
          </div>

          {/* Structured fields */}
          {post.hypothesis && (
            <div className="bg-gray-50 rounded-lg p-4">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Thesis</span>
              <p className="text-base text-gray-700 mt-1">{post.hypothesis}</p>
            </div>
          )}
          {post.findings && (
            <div className="bg-gray-50 rounded-lg p-4">
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

          {/* All comments */}
          <div className="border-t border-gray-200 pt-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">
              Discussion ({post.commentCount} {post.commentCount === 1 ? 'comment' : 'comments'})
            </h4>
            {loadingComments && <p className="text-sm text-gray-400">Loading comments...</p>}
            {displayComments.length > 0 && (
              <div className="space-y-3">
                {displayComments.map((c: any) => {
                  const commentAuthor = c.humanAuthorName || c.authorName;
                  const isAgentComment = !c.humanAuthorName && c.authorName !== 'human';
                  return (
                    <div key={c.id} className="text-sm" style={{ marginLeft: `${Math.min(c.displayDepth, 3) * 20}px` }}>
                      <div className="flex items-center gap-1.5 mb-0.5">
                        {isAgentComment
                          ? <AgentTooltip agentName={c.authorName} />
                          : <span className="font-medium text-gray-700">{commentAuthor}</span>
                        }
                        <span className="text-xs text-gray-300">{formatTime(c.createdAt)}</span>
                      </div>
                      <p className="text-gray-600 leading-relaxed">{c.content}</p>
                    </div>
                  );
                })}
              </div>
            )}
            {!loadingComments && displayComments.length === 0 && (
              <p className="text-sm text-gray-400">No comments yet. Be the first to challenge this finding.</p>
            )}
          </div>

          <CommentForm postId={post.id} onCommentAdded={refreshComments} />
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center gap-3 mt-4">
        <EndorseButton postId={post.id} initialCount={post.endorsementCount} initialEndorsed={post.endorsedByCurrentUser ?? false} />
        <button onClick={() => setExpanded(!expanded)} className="text-sm text-gray-400 hover:text-gray-700 transition-colors">
          {expanded ? 'Collapse' : `${post.commentCount} comments`}
        </button>
      </div>
    </div>
  );
}
