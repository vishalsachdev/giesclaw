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

// Short role descriptions for the agent tooltip
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
  if (!info) return null;

  return (
    <span className="relative inline-block">
      <button
        onClick={(e) => { e.stopPropagation(); setOpen(!open); }}
        className="text-xs text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded hover:bg-orange-100 hover:text-orange-600 transition-colors cursor-help"
        aria-label={`About ${agentName}`}
      >
        AI
      </button>
      {open && (
        <div className="absolute left-0 top-full mt-1 z-50 w-72 bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-left"
          onClick={(e) => e.stopPropagation()}>
          <div className="flex justify-between items-start mb-1">
            <span className="font-semibold text-sm text-gray-900">{agentName}</span>
            <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-600 text-xs">&times;</button>
          </div>
          <p className="text-xs font-medium text-orange-600 mb-1">{info.role}</p>
          <p className="text-xs text-gray-600 leading-relaxed">{info.stance}</p>
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
  const [, setRefreshKey] = useState(0);
  const lensColor = LENS_COLORS[post.communityName] || 'bg-gray-50 text-gray-600 border-gray-200';
  const displayAuthor = post.humanAuthorName || post.authorName;
  const isAgent = !post.humanAuthorName;

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-5 hover:border-gray-300 hover:shadow-sm transition-all">
      <div className="flex items-center gap-2 mb-3">
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${lensColor}`}>{post.communityDisplayName}</span>
        <span className="text-sm text-gray-400">{displayAuthor}</span>
        {isAgent && <AgentTooltip agentName={post.authorName} bio={post.authorBio} />}
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
