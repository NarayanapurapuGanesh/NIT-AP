import type { Metadata } from 'next';
import './globals.css';
import '@/styles/globals.css';
import { Providers } from '@/components/providers';

export const metadata: Metadata = {
  title: 'FacultyIQ | Enterprise AI Faculty Recruitment Platform',
  description: 'Offline-first, AI-native, production-grade faculty recruitment platform for universities.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 font-sans antialiased min-h-screen">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
