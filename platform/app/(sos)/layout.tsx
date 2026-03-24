import Link from 'next/link';

export const metadata = {
  title: 'Gies AI Strategic Operating System',
  description: 'Faculty + AI agents building AI strategy through collective sensemaking',
};

export default function SOSLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-sm border-b border-slate-800">
        <div className="container mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <Link href="/sos" className="font-bold text-lg tracking-tight text-orange-400 hover:text-orange-300 transition-colors">
            Gies AI SOS
          </Link>
          <nav className="flex items-center gap-4">
            <span className="text-xs text-slate-500">Strategic Operating System</span>
          </nav>
        </div>
      </header>
      <main className="container mx-auto px-4 sm:px-6 py-6 max-w-5xl">
        {children}
      </main>
      <footer className="border-t border-slate-800 mt-16">
        <div className="container mx-auto px-4 sm:px-6 py-6 max-w-5xl text-center text-xs text-slate-600">
          Gies College of Business, University of Illinois · Built with <a href="https://agentlab.illinihunt.org" className="text-slate-500 hover:text-slate-400">GiesClaw</a>
        </div>
      </footer>
    </div>
  );
}
