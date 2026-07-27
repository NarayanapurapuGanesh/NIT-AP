'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  PlayCircle, 
  FolderOpen, 
  Sparkles, 
  FileText, 
  Award, 
  Plus, 
  BarChart2, 
  UserCheck, 
  ArrowRight,
  Trash2
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { getUserSessions, seedDemoSessions, clearUserSessions, CandidateEvaluationSession } from '@/lib/session-store';

export default function DashboardPage() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<CandidateEvaluationSession[]>([]);

  useEffect(() => {
    if (user?.email) {
      const userPastSessions = getUserSessions(user.email);
      setSessions(userPastSessions);
    }
  }, [user]);

  const handleLoadDemoData = () => {
    if (!user?.email) return;
    const demo = seedDemoSessions(user.email);
    setSessions(demo);
  };

  const handleClearSessions = () => {
    if (!user?.email) return;
    clearUserSessions(user.email);
    setSessions([]);
  };

  const hasSessions = sessions.length > 0;

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* 1. START INTERVIEW SECTION */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-sky-950/90 via-slate-900 to-indigo-950/90 border border-sky-500/30 shadow-xl backdrop-blur-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Multi-Agent Candidate Evaluation</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Start New Candidate Interview Session
          </h1>
          <p className="text-xs text-slate-400">
            Select job position & resume to launch sequential evaluation (Resume Analyser &rarr; Demo Video Analysis &rarr; Coding Test &rarr; Live Interaction Teaching Session &rarr; Report).
          </p>
        </div>

        <Link href="/dashboard/evaluation-session">
          <Button className="bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs px-5 py-3 flex items-center space-x-2 shadow-lg shadow-sky-600/30">
            <PlayCircle className="h-4 w-4" />
            <span>Start Interview Session</span>
          </Button>
        </Link>
      </div>

      {/* 2. MAIN SECTION: REPORTS & HISTORY */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center">
            <FileText className="h-5 w-5 text-sky-400 mr-2" />
            Candidate Evaluation Reports
          </h2>
          {hasSessions && (
            <div className="flex items-center space-x-3">
              <span className="text-xs text-slate-400">
                Showing {sessions.length} recorded report(s)
              </span>
              <Button
                onClick={handleClearSessions}
                variant="outline"
                className="text-xs border-red-500/30 text-red-400 hover:bg-red-500/10 flex items-center space-x-1 py-1 px-2.5"
              >
                <Trash2 className="h-3.5 w-3.5" />
                <span>Clear All Uploads & Reports</span>
              </Button>
            </div>
          )}
        </div>

        {/* NEW USER VIEW: EMPTY BOXES */}
        {!hasSessions ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Empty Box 1: Past Reports */}
            <Card className="border-slate-800 bg-slate-900/40 border-dashed backdrop-blur-md p-8 text-center space-y-4 flex flex-col items-center justify-center min-h-[220px]">
              <div className="h-12 w-12 rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-slate-500">
                <FolderOpen className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-semibold text-white">No Previous Reports Available</h3>
                <p className="text-xs text-slate-400 max-w-xs">
                  Your evaluation report history is currently empty. Start a new interview session above to generate AI candidate reports.
                </p>
              </div>
            </Card>

            {/* Empty Box 2: Recent Analytics & Demo Data option */}
            <Card className="border-slate-800 bg-slate-900/40 border-dashed backdrop-blur-md p-8 text-center space-y-4 flex flex-col items-center justify-center min-h-[220px]">
              <div className="h-12 w-12 rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center text-slate-500">
                <BarChart2 className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <h3 className="text-sm font-semibold text-white">Score & Performance Metrics</h3>
                <p className="text-xs text-slate-400 max-w-xs">
                  Scores will populate automatically once interview sessions are closed.
                </p>
              </div>
              <Button
                onClick={handleLoadDemoData}
                variant="outline"
                className="text-xs border-slate-700 text-slate-300 hover:bg-slate-800 flex items-center space-x-1.5 mt-2"
              >
                <Sparkles className="h-3.5 w-3.5 text-amber-400" />
                <span>Load Sample Demo Reports</span>
              </Button>
            </Card>
          </div>
        ) : (
          /* RETURNING USER VIEW: OLD REPORTS LIST */
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4">
              {sessions.map((report) => (
                <Card key={report.id} className="border-slate-800 bg-slate-900/60 backdrop-blur-md p-5 hover:border-slate-700 transition-colors">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div className="flex items-center space-x-4">
                      <div className="h-11 w-11 rounded-2xl bg-sky-600/20 border border-sky-500/30 flex items-center justify-center font-bold text-sm text-sky-400">
                        {report.candidateName.split(' ')[1]?.[0] || 'C'}
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white">{report.candidateName}</h3>
                        <p className="text-xs text-slate-400">
                          {report.department} &bull; <span className="text-sky-300 font-medium">{report.appliedRank}</span>
                        </p>
                        <p className="text-[11px] text-slate-500 mt-0.5">
                          Evaluated: {new Date(report.createdAt).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-6 w-full sm:w-auto justify-between sm:justify-end border-t sm:border-t-0 border-slate-800 pt-3 sm:pt-0">
                      <div className="text-right">
                        <span className="text-xs text-slate-400 block font-medium">Overall Score</span>
                        <span className="text-xl font-bold text-emerald-400 font-mono">
                          {report.scores.overallScore} / 100
                        </span>
                      </div>

                      <div className="flex items-center space-x-3">
                        <span className="text-xs px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                          {report.recommendation}
                        </span>

                        <Link href="/dashboard/evaluation-session">
                          <Button variant="outline" className="text-xs border-slate-700 text-slate-200 hover:bg-slate-800 flex items-center space-x-1 py-1.5 px-3">
                            <span>View Full Report</span>
                            <ArrowRight className="h-3.5 w-3.5 text-sky-400" />
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
