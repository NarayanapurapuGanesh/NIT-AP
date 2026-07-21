import React from 'react';
import Link from 'next/link';
import { LayoutDashboard, Users, FileText, Settings, Cpu, Bell } from 'lucide-react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/80 bg-slate-900/60 flex flex-col backdrop-blur-xl">
        <div className="flex h-16 items-center px-6 border-b border-slate-800/80 space-x-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-600 text-white shadow-md shadow-sky-600/20">
            <Cpu className="h-5 w-5" />
          </div>
          <span className="text-lg font-bold text-white tracking-tight">FacultyIQ</span>
        </div>

        <nav className="flex-1 p-4 space-y-1 text-sm font-medium">
          <Link
            href="/dashboard"
            className="flex items-center space-x-3 rounded-lg bg-sky-600/10 text-sky-400 px-3 py-2.5 transition-colors border border-sky-500/20"
          >
            <LayoutDashboard className="h-4 w-4" />
            <span>Overview</span>
          </Link>
          <div className="pt-4 pb-1 px-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Recruitment Foundation
          </div>
          <Link
            href="#"
            className="flex items-center space-x-3 rounded-lg text-slate-400 hover:bg-slate-800/60 hover:text-white px-3 py-2.5 transition-colors opacity-60 cursor-not-allowed"
          >
            <Users className="h-4 w-4" />
            <span>Candidates (Phase 2)</span>
          </Link>
          <Link
            href="#"
            className="flex items-center space-x-3 rounded-lg text-slate-400 hover:bg-slate-800/60 hover:text-white px-3 py-2.5 transition-colors opacity-60 cursor-not-allowed"
          >
            <FileText className="h-4 w-4" />
            <span>Dossiers (Phase 3)</span>
          </Link>
          <Link
            href="#"
            className="flex items-center space-x-3 rounded-lg text-slate-400 hover:bg-slate-800/60 hover:text-white px-3 py-2.5 transition-colors opacity-60 cursor-not-allowed"
          >
            <Settings className="h-4 w-4" />
            <span>Settings</span>
          </Link>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 px-8 flex items-center justify-between backdrop-blur-xl">
          <h2 className="text-base font-semibold text-white">Institutional Workspace</h2>
          <div className="flex items-center space-x-4">
            <button className="relative rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors">
              <Bell className="h-4 w-4" />
            </button>
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-bold text-xs text-white">
              UN
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}
