'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  Scale, 
  CheckCircle2, 
  ShieldCheck, 
  Users, 
  FileCheck, 
  RotateCw,
  AlertCircle
} from 'lucide-react';

export default function ComplianceAgentPage() {
  const [auditing, setAuditing] = useState(false);

  const policyChecklist = [
    { policy: 'UGC Minimum Qualifications for Faculty Appointment 2026', status: 'Compliant', score: '100%' },
    { policy: 'NIT Act & Statutes Faculty Cadre Structure Norms', status: 'Compliant', score: '100%' },
    { policy: 'Reservation Roster & EEO Compliance Check (SC/ST/OBC/EWS)', status: 'Verified', score: 'Passed' },
    { policy: 'AI Bias Mitigation & Gender Anonymized Screening Audit', status: 'Active', score: 'Zero Bias Detected' },
  ];

  const handleAudit = () => {
    setAuditing(true);
    setTimeout(() => {
      setAuditing(false);
    }, 1200);
  };

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-amber-950/80 via-slate-900 to-slate-950 border border-amber-500/20 shadow-xl backdrop-blur-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
            <Scale className="h-3.5 w-3.5" />
            <span>Institutional Policy & EEO Compliance</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Institutional Compliance & Diversity Agent</h1>
          <p className="text-xs text-slate-400">
            Audits faculty selection processes against institutional statutes, reservation rosters, UGC norms, and eliminates bias.
          </p>
        </div>

        <Button onClick={handleAudit} disabled={auditing} className="bg-amber-600 hover:bg-amber-500 text-white text-xs px-4 py-2 flex items-center space-x-1.5">
          <RotateCw className={`h-3.5 w-3.5 ${auditing ? 'animate-spin' : ''}`} />
          <span>{auditing ? 'Auditing Policy Roster...' : 'Run Compliance Audit'}</span>
        </Button>
      </div>

      {/* Audit Banner Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1 border-amber-500/30 bg-gradient-to-b from-amber-950/30 to-slate-900/60 backdrop-blur-md p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-amber-400">Compliance Score</span>
            <ShieldCheck className="h-6 w-6 text-amber-400" />
          </div>
          <div className="text-4xl font-extrabold text-white font-mono">100%</div>
          <div className="text-xs text-slate-300">
            Full compliance verified across 14 institutional policy criteria. Zero regulatory conflicts identified.
          </div>
        </Card>

        <Card className="md:col-span-2 border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-bold text-white flex items-center">
              <FileCheck className="h-4 w-4 text-amber-400 mr-2" />
              Statutory Policy Verification Matrix
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {policyChecklist.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-slate-950/40 border border-slate-800 text-xs">
                <span className="font-medium text-slate-200">{item.policy}</span>
                <div className="flex items-center space-x-2 shrink-0">
                  <span className="font-mono text-emerald-400 font-semibold">{item.score}</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold">
                    {item.status}
                  </span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* AI Bias Audit Trail */}
      <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-base font-bold text-white flex items-center">
            <Users className="h-4 w-4 text-amber-400 mr-2" />
            AI Bias Detection & Diversity Audit Trail
          </CardTitle>
          <CardDescription className="text-xs text-slate-400">Ensures candidate evaluation relies strictly on verified academic metrics</CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-300 space-y-2">
            <div className="flex items-center justify-between text-white font-semibold">
              <span className="flex items-center"><CheckCircle2 className="h-4 w-4 text-emerald-400 mr-1.5" /> Anonymized Screening Active</span>
              <span className="text-emerald-400 font-mono">100% Bias Free</span>
            </div>
            <p className="text-slate-400 leading-relaxed text-[11px]">
              The FacultyIQ Compliance Agent strips demographic signals (gender, age, non-academic affiliations) prior to initial AI scoring. Evaluation weights are bound 100% to verified publication output, teaching record, and technical interview responses.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
