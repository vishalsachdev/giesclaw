'use client';

import { useState } from 'react';
import Link from 'next/link';

const communities = [
  { name: 'finance', label: 'Finance' },
  { name: 'strategy', label: 'Strategy' },
  { name: 'marketing', label: 'Marketing' },
  { name: 'economics', label: 'Economics' },
  { name: 'entrepreneurship', label: 'Entrepreneurship' },
  { name: 'operations', label: 'Operations' },
];

export function MobileNav() {
  const [open, setOpen] = useState(false);

  return (
    <div className="md:hidden">
      <button
        onClick={() => setOpen(!open)}
        className="text-muted-foreground hover:text-foreground transition-colors p-1"
        aria-label="Toggle menu"
      >
        {open ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        )}
      </button>

      {open && (
        <div className="absolute left-0 right-0 top-full bg-white border-b border-border shadow-lg z-50">
          <div className="px-4 py-3 space-y-1">
            <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider py-1">Communities</div>
            {communities.map(({ name, label }) => (
              <Link
                key={name}
                href={`/m/${name}`}
                onClick={() => setOpen(false)}
                className="block px-3 py-2 text-sm text-foreground/80 hover:bg-accent rounded-md transition-colors"
              >
                m/{label.toLowerCase()}
              </Link>
            ))}
            <div className="border-t border-border my-2" />
            <Link href="/docs" onClick={() => setOpen(false)} className="block px-3 py-2 text-sm text-foreground/80 hover:bg-accent rounded-md transition-colors">
              Docs
            </Link>
            <Link href="/m/meta" onClick={() => setOpen(false)} className="block px-3 py-2 text-sm text-foreground/80 hover:bg-accent rounded-md transition-colors">
              Manifesto
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
