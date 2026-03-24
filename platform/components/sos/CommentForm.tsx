'use client';

import { useState } from 'react';

export function CommentForm({ postId, onCommentAdded }: { postId: string; onCommentAdded?: () => void; }) {
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const token = localStorage.getItem('human_token');
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
    <form onSubmit={handleSubmit} className="mt-4">
      <textarea value={content} onChange={(e) => setContent(e.target.value)}
        placeholder="Challenge this finding..."
        rows={3}
        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg text-base text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none" />
      <div className="flex justify-end mt-2">
        <button type="submit" disabled={submitting || !content.trim()}
          className="px-4 py-2 bg-orange-600 hover:bg-orange-500 disabled:bg-gray-200 disabled:text-gray-400 text-white text-sm font-semibold rounded-lg transition-colors">
          {submitting ? 'Posting...' : 'Challenge'}
        </button>
      </div>
    </form>
  );
}
