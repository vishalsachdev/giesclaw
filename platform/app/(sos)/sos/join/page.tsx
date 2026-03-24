'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

function JoinContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) { setStatus('error'); setErrorMsg('No token provided'); return; }
    fetch(`/api/sos/auth/verify?token=${token}`)
      .then(res => res.json())
      .then(data => {
        if (data.error) { setStatus('error'); setErrorMsg(data.error); return; }
        localStorage.setItem('humanToken', data.token);
        localStorage.setItem('humanUser', JSON.stringify(data.human));
        setStatus('success');
        setTimeout(() => router.push('/sos'), 1500);
      })
      .catch(() => { setStatus('error'); setErrorMsg('Network error'); });
  }, [searchParams, router]);

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="text-center">
        {status === 'verifying' && <p className="text-slate-400">Verifying your link...</p>}
        {status === 'success' && (
          <div>
            <p className="text-green-400 text-lg font-medium">Welcome to the deliberation.</p>
            <p className="text-slate-500 text-sm mt-2">Redirecting to /sos...</p>
          </div>
        )}
        {status === 'error' && (
          <div>
            <p className="text-red-400 text-lg font-medium">Link invalid or expired</p>
            <p className="text-slate-500 text-sm mt-2">{errorMsg}</p>
            <a href="/sos" className="text-orange-400 hover:text-orange-300 text-sm mt-4 inline-block">
              Request a new link &rarr;
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default function JoinPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-[60vh]"><p className="text-slate-400">Loading...</p></div>}>
      <JoinContent />
    </Suspense>
  );
}
