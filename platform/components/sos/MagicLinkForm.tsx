'use client';

import { useState } from 'react';

export function MagicLinkForm() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const [magicUrl, setMagicUrl] = useState('');

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
      if (data.magicUrl) setMagicUrl(data.magicUrl);
      setStatus('sent');
    } catch {
      setErrorMsg('Network error');
      setStatus('error');
    }
  }

  if (status === 'sent') {
    return (
      <div className="text-center py-4 px-6 bg-green-50 border border-green-200 rounded-xl max-w-md mx-auto">
        <p className="text-green-700 text-base font-medium">
          {magicUrl ? (
            <a href={magicUrl} className="underline hover:text-green-600">Click here to enter the deliberation</a>
          ) : (
            'Check your email for the login link.'
          )}
        </p>
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
        className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg text-base text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
      />
      <button
        type="submit"
        disabled={status === 'sending'}
        className="px-6 py-3 bg-orange-600 hover:bg-orange-500 disabled:bg-gray-300 text-white text-base font-semibold rounded-lg transition-colors"
      >
        {status === 'sending' ? 'Sending...' : 'Join'}
      </button>
      {errorMsg && <p className="text-red-500 text-sm mt-1">{errorMsg}</p>}
    </form>
  );
}
