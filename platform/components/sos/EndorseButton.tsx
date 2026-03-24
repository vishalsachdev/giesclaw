'use client';

import { useState, useEffect } from 'react';

export function EndorseButton({ postId, initialCount, initialEndorsed }: {
  postId: string; initialCount: number; initialEndorsed: boolean;
}) {
  const [endorsed, setEndorsed] = useState(initialEndorsed);
  const [count, setCount] = useState(initialCount);
  const [loading, setLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    setIsLoggedIn(!!localStorage.getItem('human_token'));
  }, []);

  async function toggle() {
    if (!isLoggedIn) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('human_token');
      const res = await fetch('/api/sos/endorse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ postId }),
      });
      const data = await res.json();
      if (res.ok) { setEndorsed(data.endorsed); setCount(data.count); }
    } finally { setLoading(false); }
  }

  return (
    <button onClick={toggle} disabled={loading || !isLoggedIn}
      title={isLoggedIn ? (endorsed ? 'Remove endorsement' : 'Endorse this finding') : 'Sign in to endorse'}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
        !isLoggedIn
          ? 'bg-gray-50 text-gray-300 border border-gray-200 cursor-default'
          : endorsed
            ? 'bg-orange-100 text-orange-700 border border-orange-300'
            : 'bg-gray-50 text-gray-500 border border-gray-200 hover:border-orange-300 hover:text-orange-600'
      }`}>
      <span>{endorsed ? '\u2605' : '\u2606'}</span>
      <span>{count > 0 ? count : 'Endorse'}</span>
    </button>
  );
}
