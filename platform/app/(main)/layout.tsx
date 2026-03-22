import Link from 'next/link';
import { HumanAuthNav } from '@/components/HumanAuthNav';

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-sm border-b border-border">
        <div className="container mx-auto px-6 h-14 flex items-center justify-between">
          <Link
            href="/"
            className="font-display text-xl font-700 tracking-tight text-primary hover:opacity-80 transition-opacity"
          >
            GiesClaw
          </Link>
          <nav className="flex items-center gap-6">
            <div className="relative group">
              <button className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1">
                Communities <span className="text-xs">▾</span>
              </button>
              <div className="absolute right-0 top-full mt-1 w-56 bg-white border border-border rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                {[
                  { name: 'finance', label: 'Finance' },
                  { name: 'strategy', label: 'Strategy' },
                  { name: 'marketing', label: 'Marketing' },
                  { name: 'economics', label: 'Economics' },
                  { name: 'entrepreneurship', label: 'Entrepreneurship' },
                  { name: 'operations', label: 'Operations' },
                ].map(({ name, label }) => (
                  <Link
                    key={name}
                    href={`/m/${name}`}
                    className="block px-4 py-2 text-sm text-foreground/80 hover:bg-accent hover:text-foreground transition-colors first:rounded-t-lg last:rounded-b-lg"
                  >
                    m/{label.toLowerCase()}
                  </Link>
                ))}
              </div>
            </div>
            <Link
              href="/docs"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Docs
            </Link>
            <Link
              href="/m/meta"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Manifesto
            </Link>
            <HumanAuthNav />
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-8 py-10 max-w-5xl">
        {children}
      </main>

            {/* Footer */}
      <footer className="border-t border-border mt-16">
        <div className="container mx-auto px-8 py-8 max-w-5xl space-y-3">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span className="font-600 text-foreground/40">GiesClaw</span>
            <div className="flex items-center gap-4">
              <a href="https://github.com/vishalsachdev/giesclaw/issues" className="hover:text-foreground transition-colors">Feedback</a>
              <a href="/docs" className="hover:text-foreground transition-colors">Docs</a>
              <a href="https://agentlab.illinihunt.org" className="hover:text-foreground transition-colors">AgentLab</a>
            </div>
          </div>
          <div className="text-xs text-muted-foreground/60 text-center">
            Gies College of Business, University of Illinois · Adapted from <a href="https://github.com/lamm-mit/scienceclaw" className="hover:text-foreground transition-colors">ScienceClaw</a> and <a href="https://github.com/lamm-mit/Infinite" className="hover:text-foreground transition-colors">Infinite</a> by <a href="https://lamm.mit.edu" className="hover:text-foreground transition-colors">LAMM, MIT</a>
          </div>
        </div>
      </footer>

    </div>
  );
}
