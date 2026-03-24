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
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
        endorsed
          ? 'bg-orange-100 text-orange-700 border border-orange-300'
          : 'bg-gray-50 text-gray-500 border border-gray-200 hover:border-orange-300 hover:text-orange-600'
      }`}>
      <span>{endorsed ? '\u2605' : '\u2606'}</span>
      <span>{count > 0 ? count : 'Endorse'}</span>
    </button>
  );
}
