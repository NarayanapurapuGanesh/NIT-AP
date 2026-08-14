'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { 
  LayoutDashboard, 
  FileText, 
  Video, 
  Microscope, 
  Scale, 
  Users, 
  Cpu, 
  Bell, 
  LogOut,
  Sparkles,
  PlayCircle,
  User,
  CheckSquare,
  Code2,
  MessageSquareMore
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const initials = user
    ? `${user.firstName?.[0] || ''}${user.lastName?.[0] || ''}`.toUpperCase() || 'U'
    : 'U';

  const fullName = user ? `${user.firstName} ${user.lastName}` : 'Faculty User';

  const mainNav = [
    { label: 'Overview Hub', href: '/dashboard', icon: LayoutDashboard },
    { label: 'Start Interview Session', href: '/dashboard/evaluation-session', icon: PlayCircle, badge: 'Active Workflow' },
    { label: 'Coding Assessment', href: '/dashboard/coding-agent', icon: Code2, badge: 'Interactive' },
    { label: 'Teaching Interaction', href: '/dashboard/interaction', icon: MessageSquareMore, badge: 'AI Agent' },
  ];

  const agentResultsNav = [
    { label: 'Resume Agent Results', href: '/dashboard/resume-agent', icon: FileText },
    { label: 'Video Analysis Results', href: '/dashboard/video-agent', icon: Video },
    { label: 'Candidate Dossiers & Reports', href: '/dashboard/candidates', icon: Users },
  ];

  const accountNav = [
    { label: 'Edit Profile & Settings', href: '/dashboard/profile', icon: User },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/80 bg-slate-900/70 flex flex-col backdrop-blur-xl shrink-0">
        {/* Brand Header */}
        <div className="flex h-16 items-center px-5 border-b border-slate-800/80 space-x-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-md shadow-sky-600/20">
            <Cpu className="h-5 w-5" />
          </div>
          <div>
            <span className="text-base font-bold text-white tracking-tight flex items-center">
              FacultyIQ <Sparkles className="h-3 w-3 text-sky-400 ml-1.5" />
            </span>
            <span className="text-[10px] text-sky-400 block font-medium">Enterprise AI Recruitment</span>
          </div>
        </div>

        {/* Navigation Bar */}
        <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto text-sm font-medium">
          {/* Main Navigation */}
          <div className="space-y-1">
            <div className="px-3 pb-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              Main Navigation
            </div>
            {mainNav.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-2.5 rounded-lg transition-all text-xs ${
                    isActive
                      ? 'bg-sky-600/15 text-sky-400 border border-sky-500/30 font-semibold shadow-sm shadow-sky-950'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`h-4 w-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-semibold">
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>

          {/* View Individual Agent Results */}
          <div className="space-y-1">
            <div className="px-3 pb-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              View Agent Results
            </div>
            {agentResultsNav.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg transition-all text-xs ${
                    isActive
                      ? 'bg-sky-600/15 text-sky-400 border border-sky-500/30 font-semibold'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`h-4 w-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                </Link>
              );
            })}
          </div>

          {/* Account Settings */}
          <div className="space-y-1">
            <div className="px-3 pb-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
              Account Management
            </div>
            {accountNav.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg transition-all text-xs ${
                    isActive
                      ? 'bg-sky-600/15 text-sky-400 border border-sky-500/30 font-semibold'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`h-4 w-4 ${isActive ? 'text-sky-400' : 'text-slate-400'}`} />
                    <span>{item.label}</span>
                  </div>
                </Link>
              );
            })}
          </div>
        </nav>

        {/* User Footer */}
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/40">
          <div className="flex items-center justify-between px-2 py-1.5 rounded-lg hover:bg-slate-800/40 transition-colors">
            <Link href="/dashboard/profile" className="flex items-center space-x-2.5 overflow-hidden group">
              <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center font-bold text-xs text-white shadow-inner shrink-0">
                {initials}
              </div>
              <div className="text-xs truncate">
                <p className="font-semibold text-white truncate max-w-[110px] group-hover:text-sky-400 transition-colors">
                  {fullName}
                </p>
                <p className="text-[10px] text-slate-400 truncate max-w-[110px]">
                  {user?.academicRole || 'Faculty Committee'}
                </p>
              </div>
            </Link>
            <button
              onClick={handleLogout}
              title="Sign Out"
              className="text-slate-400 hover:text-rose-400 transition-colors p-1"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="h-16 border-b border-slate-800/80 bg-slate-950/80 px-8 flex items-center justify-between backdrop-blur-xl shrink-0">
          <div>
            <h2 className="text-sm font-semibold text-white flex items-center">
              NIT Andhra Pradesh — Faculty Recruitment Cell
            </h2>
            <p className="text-[11px] text-slate-400">
              Logged in user: <span className="text-sky-400 font-semibold">{fullName}</span> ({user?.email || 'Active Session'})
            </p>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full text-[11px] font-medium text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>All AI Agents Online</span>
            </div>
            <button className="relative rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors">
              <Bell className="h-4 w-4" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-sky-400"></span>
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}
