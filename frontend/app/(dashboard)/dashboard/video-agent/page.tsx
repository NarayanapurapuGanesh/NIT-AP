'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  Video, 
  Play, 
  Sparkles, 
  MessageSquare, 
  Volume2, 
  CheckCircle2, 
  Sliders,
  RotateCw,
  Clock
} from 'lucide-react';

export default function VideoAgentPage() {
  const [activeTab, setActiveTab] = useState<'transcript' | 'metrics'>('metrics');
  const [processing, setProcessing] = useState(false);

  const softSkills = [
    { metric: 'Pedagogical & Teaching Clarity', score: 92, status: 'Exceptional' },
    { metric: 'Subject Matter Mastery', score: 95, status: 'Top 5%' },
    { metric: 'Communication & Articulation', score: 88, status: 'Strong' },
    { metric: 'Professional Confidence & Demeanor', score: 90, status: 'Very High' },
    { metric: 'Q&A Responsiveness under Pressure', score: 86, status: 'Good' },
  ];

  const transcriptHighlights = [
    { time: '01:45', topic: 'Pedagogical Vision & Micro-Services Teaching Approach', text: 'When introducing distributed systems to undergraduates, I start with physical analogies like bank ledger replicas before formalizing Paxos or Raft...' },
    { time: '06:12', topic: 'Research Roadmap & Future Grant Strategy', text: 'Our next 3-year focus will be on edge AI inference optimization for resource-constrained IoT nodes, leveraging quantization...' },
    { time: '12:30', topic: 'Diversity & Mentorship Commitment', text: 'I actively mentor female undergraduate researchers, resulting in two student papers at IEEE SECON...' },
  ];

  const handleReanalyze = () => {
    setProcessing(true);
    setTimeout(() => {
      setProcessing(false);
    }, 1200);
  };

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-950 border border-indigo-500/20 shadow-xl backdrop-blur-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
            <Video className="h-3.5 w-3.5" />
            <span>Multimodal AI Agent</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Video & Interview Analysis Agent</h1>
          <p className="text-xs text-slate-400">
            Processes interview recordings, evaluates pedagogical clarity, communication skills, and generates synced transcripts.
          </p>
        </div>

        <Button onClick={handleReanalyze} disabled={processing} className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-4 py-2 flex items-center space-x-1.5">
          <RotateCw className={`h-3.5 w-3.5 ${processing ? 'animate-spin' : ''}`} />
          <span>{processing ? 'Analyzing Video...' : 'Run Video Analysis Agent'}</span>
        </Button>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Video Player Mockup */}
        <div className="space-y-6">
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md overflow-hidden">
            <div className="relative aspect-video bg-slate-950 border-b border-slate-800 flex items-center justify-center group cursor-pointer">
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent"></div>
              
              <div className="h-14 w-14 rounded-full bg-indigo-600/90 text-white flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <Play className="h-6 w-6 fill-current ml-1" />
              </div>

              <div className="absolute bottom-3 left-4 right-4 flex items-center justify-between text-xs text-white">
                <span className="font-semibold text-slate-200">Interview Session — Dr. Aris Thorne</span>
                <span className="font-mono text-slate-400 text-[11px]">18:42 / 25:00</span>
              </div>
            </div>

            <CardContent className="p-4 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center"><Volume2 className="h-3.5 w-3.5 text-indigo-400 mr-1" /> Audio Clarity: 98%</span>
                <span className="flex items-center"><Clock className="h-3.5 w-3.5 text-sky-400 mr-1" /> Duration: 25 mins</span>
              </div>
            </CardContent>
          </Card>

          {/* AI Overall Soft Skills Card */}
          <Card className="border-indigo-500/30 bg-gradient-to-b from-indigo-950/30 to-slate-900/60 backdrop-blur-md">
            <CardHeader className="pb-2">
              <span className="text-[10px] uppercase tracking-wider text-indigo-400 font-bold">Aggregate Soft Skills Index</span>
              <div className="flex items-baseline space-x-2">
                <span className="text-4xl font-extrabold text-white font-mono">90.2</span>
                <span className="text-sm text-slate-400 font-semibold">/ 100</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div className="bg-gradient-to-r from-indigo-500 to-purple-400 h-full rounded-full" style={{ width: '90.2%' }}></div>
              </div>
              <p className="text-[11px] text-slate-400 pt-1">
                Candidate exhibits high articulate confidence, structured pedagogical breakdown, and clear research articulation.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Metrics & Transcript Tabs */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
            <CardHeader className="flex flex-row items-center justify-between pb-4">
              <div>
                <CardTitle className="text-base font-bold text-white flex items-center">
                  <Sparkles className="h-4 w-4 text-indigo-400 mr-2" />
                  Multimodal Agent Diagnostics
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">Soft-skills radar scoring and timestamped audio transcription</CardDescription>
              </div>

              <div className="flex space-x-1 p-1 bg-slate-950/80 rounded-lg border border-slate-800 text-xs">
                <button
                  onClick={() => setActiveTab('metrics')}
                  className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'metrics' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'}`}
                >
                  Radar Metrics
                </button>
                <button
                  onClick={() => setActiveTab('transcript')}
                  className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'transcript' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'}`}
                >
                  Transcript Sync
                </button>
              </div>
            </CardHeader>

            <CardContent>
              {activeTab === 'metrics' ? (
                <div className="space-y-4">
                  {softSkills.map((skill, idx) => (
                    <div key={idx} className="space-y-1.5 p-3 rounded-xl bg-slate-950/40 border border-slate-800/80">
                      <div className="flex justify-between text-xs">
                        <span className="font-semibold text-slate-200">{skill.metric}</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-[10px] text-indigo-400 font-semibold px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">{skill.status}</span>
                          <span className="font-mono text-white font-bold">{skill.score}%</span>
                        </div>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-gradient-to-r from-indigo-500 to-sky-400 h-full rounded-full" style={{ width: `${skill.score}%` }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-3">
                  {transcriptHighlights.map((item, idx) => (
                    <div key={idx} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 transition-colors space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-indigo-300 flex items-center">
                          <MessageSquare className="h-3.5 w-3.5 mr-1.5 text-indigo-400" />
                          {item.topic}
                        </span>
                        <span className="font-mono text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                          {item.time}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 italic pt-1 leading-relaxed pl-5 border-l-2 border-indigo-500/40">
                        &quot;{item.text}&quot;
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Committee Recommendation */}
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md p-4">
            <div className="flex items-start space-x-3 text-xs text-slate-300">
              <CheckCircle2 className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-white block mb-0.5">Selection Committee Recommendation: Pass to Final Round</span>
                <span>Candidate demonstrated exemplary pedagogical clarity and high confidence during Q&A handling.</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
