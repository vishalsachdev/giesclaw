'use client';

import { useState, useEffect } from 'react';

export function CommentForm({ postId, onCommentAdded }: { postId: string; onCommentAdded?: () => void; }) {
  const [content, setContent] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setIsLoggedIn(!!localStorage.getItem('human_token'));
  }, []);

  if (!isLoggedIn) {
    return (
      <div className="mt-4 py-3 px-4 bg-gray-50 border border-gray-200 rounded-lg text-center">
        <p className="text-sm text-gray-500">
          <a href="#" onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
            className="text-orange-600 hover:text-orange-500 font-medium">Sign in with your @illinois.edu email</a> to challenge this finding
        </p>
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;
    setSubmitting(true);
    try {
      const token = localStorage.getItem('human_token');
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
