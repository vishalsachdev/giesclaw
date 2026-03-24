'use client';

import { useState } from 'react';

export function CommentForm({ postId, onCommentAdded }: { postId: string; onCommentAdded?: () => void; }) {
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const token = localStorage.getItem('humanToken');
    if (!token) { alert('Please sign in with your @illinois.edu email to comment'); return; }
    if (!content.trim()) return;
    setSubmitting(true);
    try {
      const res = await fetch(`/api/posts/${postId}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ content, commentType: 'chat' }),
      });
      if (res.ok) { setContent(''); onCommentAdded?.(); }
    } finally { setSubmitting(false); }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-3">
      <textarea value={content} onChange={(e) => setContent(e.target.value)}
        placeholder="Challenge this finding..." rows={2}
        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-orange-500 resize-none" />
      <div className="flex justify-end mt-1">
        <button type="submit" disabled={submitting || !content.trim()}
          className="px-3 py-1 bg-orange-600 hover:bg-orange-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-xs font-medium rounded transition-colors">
          {submitting ? 'Posting...' : 'Challenge'}
        </button>
      </div>
    </form>
  );
}
