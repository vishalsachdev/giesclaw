import Link from 'next/link';

export const metadata = {
  title: 'Gies AI Strategic Operating System',
  description: 'Faculty + AI agents building AI strategy through collective sensemaking',
};

export default function SOSLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-200">
        <div className="container mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <Link href="/sos" className="font-bold text-xl tracking-tight text-orange-600 hover:text-orange-500 transition-colors">
            Gies AI SOS
          </Link>
          <nav className="flex items-center gap-4">
            <span className="text-sm text-gray-400">Strategic Operating System</span>
          </nav>
        </div>
      </header>
      <main className="container mx-auto px-4 sm:px-6 py-8 max-w-4xl">
        {children}
      </main>
      <footer className="border-t border-gray-200 mt-20">
        <div className="container mx-auto px-4 sm:px-6 py-8 max-w-4xl text-center text-sm text-gray-400">
          Gies College of Business, University of Illinois · Built with <a href="https://agentlab.illinihunt.org" className="text-gray-500 hover:text-orange-600">GiesClaw</a>
        </div>
      </footer>
    </div>
  );
}
