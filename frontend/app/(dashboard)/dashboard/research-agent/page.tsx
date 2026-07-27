'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  Microscope, 
  CheckCircle2, 
  Award, 
  BookOpen, 
  ExternalLink, 
  ShieldCheck, 
  RotateCw,
  Search,
  AlertTriangle
} from 'lucide-react';

export default function ResearchAgentPage() {
  const [verifying, setVerifying] = useState(false);

  const publications = [
    {
      title: 'Paxos Made Transparent: High-Throughput Consensus for Geo-Replicated Stores',
      journal: 'ACM Transactions on Computer Systems (TOCS)',
      year: 2024,
      citations: 142,
      quartile: 'Q1 (Top 2%)',
      impact: 'IF: 4.85',
      verified: true,
      predatory: false,
    },
    {
      title: 'Quantized Edge Inference: Zero-Copy Memory Management in Heterogeneous Clusters',
      journal: 'IEEE Transactions on Parallel & Distributed Systems (TPDS)',
      year: 2023,
      citations: 98,
      quartile: 'Q1',
      impact: 'IF: 5.30',
      verified: true,
      predatory: false,
    },
    {
      title: 'Fault Tolerant Distributed Ledger Architectures for Microgrid Energy Trading',
      journal: 'USENIX Annual Technical Conference (ATC)',
      year: 2022,
      citations: 76,
      quartile: 'CORE A*',
      impact: 'Top Conference',
      verified: true,
      predatory: false,
    },
  ];

  const handleVerify = () => {
    setVerifying(true);
    setTimeout(() => {
      setVerifying(false);
    }, 1200);
  };

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-emerald-950/80 via-slate-900 to-slate-950 border border-emerald-500/20 shadow-xl backdrop-blur-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
            <Microscope className="h-3.5 w-3.5" />
            <span>Scopus & WoS Verified</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Research & Publication Verification Agent</h1>
          <p className="text-xs text-slate-400">
            Validates research papers, verifies h-index citations, checks for predatory journals, and computes impact factor scores.
          </p>
        </div>

        <Button onClick={handleVerify} disabled={verifying} className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-4 py-2 flex items-center space-x-1.5">
          <RotateCw className={`h-3.5 w-3.5 ${verifying ? 'animate-spin' : ''}`} />
          <span>{verifying ? 'Cross-Referencing Scopus...' : 'Verify Scopus & WoS'}</span>
        </Button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <span className="text-xs font-medium text-slate-400">Verified Publications</span>
          <div className="mt-2 text-2xl font-bold text-white font-mono">34 Papers</div>
          <div className="text-[11px] text-emerald-400 mt-1 flex items-center">
            <CheckCircle2 className="h-3 w-3 mr-1" /> 100% Scopus Indexed
          </div>
        </Card>

        <Card className="p-4 border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <span className="text-xs font-medium text-slate-400">h-index / i10-index</span>
          <div className="mt-2 text-2xl font-bold text-white font-mono">18 / 24</div>
          <div className="text-[11px] text-slate-500 mt-1">Cross-verified via Google Scholar</div>
        </Card>

        <Card className="p-4 border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <span className="text-xs font-medium text-slate-400">Total Citation Count</span>
          <div className="mt-2 text-2xl font-bold text-white font-mono">1,420</div>
          <div className="text-[11px] text-sky-400 mt-1">+184 citations past year</div>
        </Card>

        <Card className="p-4 border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <span className="text-xs font-medium text-slate-400">Predatory Journal Risk</span>
          <div className="mt-2 text-2xl font-bold text-emerald-400 font-mono">0 Flags</div>
          <div className="text-[11px] text-slate-500 mt-1">Audited against UGC-CARE</div>
        </Card>
      </div>

      {/* Main Publication List Card */}
      <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-base font-bold text-white flex items-center">
              <BookOpen className="h-4 w-4 text-emerald-400 mr-2" />
              Verified Core Publications & Citations
            </CardTitle>
            <CardDescription className="text-xs text-slate-400">Scopus, WoS, and IEEE Xplore indexing verification status</CardDescription>
          </div>

          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search papers or DOIs..."
              className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
            />
          </div>
        </CardHeader>

        <CardContent>
          <div className="space-y-4">
            {publications.map((paper, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h3 className="text-sm font-bold text-white hover:text-emerald-300 cursor-pointer flex items-center">
                    {paper.title}
                    <ExternalLink className="h-3.5 w-3.5 ml-1.5 text-slate-500 hover:text-white" />
                  </h3>
                  <div className="flex items-center space-x-2 shrink-0">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {paper.quartile}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                      {paper.impact}
                    </span>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-1">
                  <span>{paper.journal} • {paper.year}</span>
                  <div className="flex items-center space-x-4">
                    <span>Citations: <strong className="text-white font-mono">{paper.citations}</strong></span>
                    <span className="text-emerald-400 flex items-center text-[11px] font-medium">
                      <ShieldCheck className="h-3.5 w-3.5 mr-1" /> Scopus Verified
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
