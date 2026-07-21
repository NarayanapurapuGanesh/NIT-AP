'use client';

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Cpu, Server, Database, Activity, CheckCircle2 } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="space-y-8 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System Infrastructure Dashboard</h1>
        <p className="text-sm text-slate-400 mt-1">
          FacultyIQ Phase 1 Engineering Foundation Status
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: 'Backend API', val: 'ASP.NET Core 9', sub: 'Clean Architecture', icon: <Server className="h-5 w-5 text-sky-400" /> },
          { label: 'Database', val: 'PostgreSQL 16', sub: 'EF Core 9 Provider', icon: <Database className="h-5 w-5 text-emerald-400" /> },
          { label: 'AI Inference', val: 'Ollama Engine', sub: 'Offline Local LLM', icon: <Cpu className="h-5 w-5 text-indigo-400" /> },
          { label: 'Health Status', val: 'System Ready', sub: 'Phase 1 Complete', icon: <Activity className="h-5 w-5 text-purple-400" /> },
        ].map((item, idx) => (
          <Card key={idx} className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-medium">{item.label}</span>
              {item.icon}
            </div>
            <div className="mt-2 text-lg font-bold text-white">{item.val}</div>
            <div className="text-xs text-slate-500 mt-0.5">{item.sub}</div>
          </Card>
        ))}
      </div>

      {/* Verification Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Architecture Verification Checklist</CardTitle>
          <CardDescription>Phase 1 core foundation modules status</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            'Monorepo root layout & 43 master documentation blueprints migrated',
            'Docker Compose container stack (PostgreSQL, Redis, Qdrant, MinIO, Ollama)',
            'ASP.NET Core 9 Web API Clean Architecture solution with CQRS & DDD base',
            'Next.js 15 App Router frontend with Tailwind CSS & Framer Motion UI library',
            'EF Core 9 PostgreSQL persistence with Auditing, Soft Delete & Repository/UnitOfWork',
          ].map((item, idx) => (
            <div key={idx} className="flex items-center space-x-3 text-sm text-slate-300">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
              <span>{item}</span>
            </div>
          ))}

          <div className="pt-4 border-t border-slate-800 flex justify-end">
            <Button variant="outline" onClick={() => window.open('https://localhost:7150/swagger', '_blank')}>
              Open Swagger API Specs
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
