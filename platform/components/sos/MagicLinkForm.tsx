'use client';

import { useState } from 'react';

export function MagicLinkForm() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus('sending');
    setErrorMsg('');
    try {
      const res = await fetch('/api/sos/auth/request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorMsg(data.error || 'Failed to send link');
        setStatus('error');
        return;
      }
      setStatus('sent');
    } catch {
      setErrorMsg('Network error');
      setStatus('error');
    }
  }

  if (status === 'sent') {
    return (
      <div className="text-center py-3 px-4 bg-green-900/30 border border-green-800 rounded-lg">
        <p className="text-green-300 text-sm">Check your email for the login link.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 max-w-md mx-auto">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="your-name@illinois.edu"
        required
        className="flex-1 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-orange-500"
      />
      <button
        type="submit"
        disabled={status === 'sending'}
        className="px-4 py-2 bg-orange-600 hover:bg-orange-500 disabled:bg-slate-700 text-white text-sm font-medium rounded-lg transition-colors"
      >
        {status === 'sending' ? 'Sending...' : 'Join'}
      </button>
      {errorMsg && <p className="text-red-400 text-xs mt-1">{errorMsg}</p>}
    </form>
  );
}
