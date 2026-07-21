import React from 'react';
import { Cpu } from 'lucide-react';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 p-6">
      <div className="w-full max-w-md space-y-6">
        <div className="flex flex-col items-center justify-center space-y-2 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-600 text-white shadow-xl shadow-sky-600/30">
            <Cpu className="h-6 w-6" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">FacultyIQ Enterprise</h1>
          <p className="text-xs text-slate-400">Institutional Faculty Recruitment Portal</p>
        </div>
        {children}
      </div>
    </div>
  );
}
