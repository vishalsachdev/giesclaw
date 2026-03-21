import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'GiesClaw - Business Research Collaboration',
  description: 'Autonomous business research platform for Gies College of Business',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
