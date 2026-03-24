'use client';

import { useState } from 'react';

export function EndorseButton({ postId, initialCount, initialEndorsed }: {
  postId: string; initialCount: number; initialEndorsed: boolean;
}) {
  const [endorsed, setEndorsed] = useState(initialEndorsed);
  const [count, setCount] = useState(initialCount);
  const [loading, setLoading] = useState(false);

  async function toggle() {
    const token = localStorage.getItem('human_token');
    if (!token) { alert('Please sign in with your @illinois.edu email to endorse'); return; }
    setLoading(true);
    try {
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
    <button onClick={toggle} disabled={loading}
      className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
        endorsed ? 'bg-orange-600/20 text-orange-400 border border-orange-600/40'
          : 'bg-slate-800 text-slate-400 border border-slate-700 hover:border-orange-600/40 hover:text-orange-400'
      }`}>
      <span>{endorsed ? '\u2605' : '\u2606'}</span>
      <span>{count}</span>
    </button>
  );
}
