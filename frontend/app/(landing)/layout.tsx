import React from 'react';
import Link from 'next/link';
import { Cpu, ShieldCheck, UserPlus } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export default function LandingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-slate-950">
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <Link href="/" className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 text-white shadow-lg shadow-sky-500/20">
              <Cpu className="h-5 w-5" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              Faculty<span className="text-sky-400">IQ</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center space-x-8 text-sm text-slate-300 font-medium">
            <Link href="#features" className="hover:text-white transition-colors">Features</Link>
            <Link href="#architecture" className="hover:text-white transition-colors">Architecture</Link>
            <Link href="#security" className="hover:text-white transition-colors">Security</Link>
          </nav>

          <div className="flex items-center space-x-3">
            <Link href="/login">
              <Button variant="ghost" size="sm" className="text-xs text-slate-300 hover:text-white">
                Sign In
              </Button>
            </Link>
            <Link href="/register">
              <Button size="sm" className="bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold px-4 py-2 flex items-center space-1.5">
                <UserPlus className="h-3.5 w-3.5 mr-1" />
                <span>Get Started</span>
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">{children}</main>

      <footer className="border-t border-slate-900 bg-slate-950 py-8">
        <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="h-4 w-4 text-sky-400" />
            <span>Offline-First Enterprise AI Faculty Recruitment Platform</span>
          </div>
          <div>© {new Date().getFullYear()} FacultyIQ Platform. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
}
