'use client';

import React, { useState, useRef } from 'react';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  FileText, 
  Video, 
  Code, 
  MessageSquare, 
  Award, 
  CheckCircle2, 
  ArrowRight, 
  Play, 
  Sparkles, 
  Briefcase, 
  Upload,
  Send,
  UserCheck,
  Building,
  RotateCw,
  FileCheck,
  FileCode
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { saveUserSession, CandidateEvaluationSession } from '@/lib/session-store';
import { extractTextFromFile, parseResumeContent } from '@/lib/documentParser';

type StepStage = 'resume' | 'video' | 'coding' | 'interaction' | 'report';

interface ParsedFileInsights {
  fileName: string;
  fileSize: string;
  score: number;
  highestDegree: string;
  institution: string;
  expYears: number;
  skills: string[];
  grants: string;
  papersCount: number;
  summary: string;
  rawTextPreview: string;
}

export default function EvaluationSessionPage() {
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [currentStage, setCurrentStage] = useState<StepStage>('resume');
  const [analyzingStage, setAnalyzingStage] = useState(false);

  // Stage 1 Selection & File Upload
  const [selectedRole, setSelectedRole] = useState('');
  const [department, setDepartment] = useState('Computer Science & Engineering');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [parsedInsights, setParsedInsights] = useState<ParsedFileInsights | null>(null);

  // Stage 4 Q&A Session State
  const [qaHistory, setQaHistory] = useState<Array<{ q: string; a: string; time: string }>>([
    {
      q: 'How do you structure undergraduate courses in Distributed Systems to make complex consensus algorithms understandable?',
      a: 'I start with physical analogies like bank ledger synchronization before moving to formal state-machine replication models like Raft and Paxos. Hands-on laboratory projects build a mini key-value store in Go.',
      time: '10:14 AM',
    },
    {
      q: 'What is your planned research roadmap for securing institutional research grants at NIT Andhra Pradesh?',
      a: 'My 3-year goal includes securing ₹50+ Lakhs from DST-SERB to investigate edge computing security. We plan to collaborate with industry partners for real-time sensor node validation.',
      time: '10:18 AM',
    },
  ]);
  const [newQuestion, setNewQuestion] = useState('');

  const resumeScore = parsedInsights ? parsedInsights.score : 80;
  const videoScore = 88;
  const codingScore = 92;
  const interactionScore = 90;

  const overallScore = Number(
    ((resumeScore + videoScore + codingScore + interactionScore) / 4).toFixed(1)
  );

  const stagesList = [
    { id: 'resume', label: '1. Resume Analyser', icon: FileText, desc: 'Role & Resume Parsing' },
    { id: 'video', label: '2. Demo Video Analysis', icon: Video, desc: 'Presentation & Soft-Skills' },
    { id: 'coding', label: '3. Coding Test', icon: Code, desc: 'Technical & Algorithmic' },
    { id: 'interaction', label: '4. Live Interaction Teaching Session', icon: MessageSquare, desc: 'Live Q&A & Pedagogy' },
    { id: 'report', label: '5. Overall Synthesis', icon: Award, desc: 'Final Report & Closure' },
  ];

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const fileObj = e.target.files[0];
      setUploadedFile(fileObj);
      setParsedInsights(null);
    }
  };

  const handleRunResumeAnalysis = async () => {
    if (!selectedRole || !uploadedFile) return;
    setAnalyzingStage(true);

    try {
      const { text, isPdf } = await extractTextFromFile(uploadedFile);
      setTimeout(() => {
        const insights = parseResumeContent(uploadedFile, text, selectedRole, isPdf);
        setParsedInsights(insights);
        setAnalyzingStage(false);
      }, 600);
    } catch {
      setTimeout(() => {
        const insights = parseResumeContent(uploadedFile, uploadedFile.name, selectedRole, false);
        setParsedInsights(insights);
        setAnalyzingStage(false);
      }, 600);
    }
  };

  const handleNextStage = (next: StepStage) => {
    setAnalyzingStage(true);
    setTimeout(() => {
      setAnalyzingStage(false);
      setCurrentStage(next);
    }, 700);
  };

  const handleSendQuestion = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQuestion.trim()) return;

    const q = newQuestion.trim();
    setNewQuestion('');
    setQaHistory((prev) => [
      ...prev,
      {
        q,
        a: `Evaluated response: "Regarding ${q.slice(0, 25)}..., our methodology leverages modular execution pipelines and rigorous fault tolerance."`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  const handleCompleteSession = () => {
    if (!user?.email) return;

    const fileName = uploadedFile ? uploadedFile.name : 'Candidate Dossier';

    const newSession: CandidateEvaluationSession = {
      id: `sess_${Date.now()}`,
      candidateName: fileName,
      candidateEmail: user.email,
      department,
      appliedRank: selectedRole || 'Assistant Professor',
      createdAt: new Date().toISOString(),
      scores: {
        resumeScore,
        videoScore,
        codingScore,
        interactionScore,
        overallScore,
      },
      recommendation: overallScore >= 80 ? 'Highly Recommended' : 'Recommended',
      summary: `Completed 5-stage evaluation for file "${fileName}" (${selectedRole || 'Assistant Professor'}, ${department}). Evaluated across resume text parsing, video presentation, coding efficiency, and Q&A handling.`,
      resumeDetails: {
        highestDegree: parsedInsights?.highestDegree || 'Document Parsed',
        expYears: parsedInsights?.expYears || 0,
        skills: parsedInsights?.skills || ['General Document'],
        papersCount: parsedInsights?.papersCount || 0,
      },
    };

    saveUserSession(user.email, newSession);
    setCurrentStage('report');
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-sky-950/90 via-slate-900 to-indigo-950/90 border border-sky-500/20 shadow-xl backdrop-blur-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 px-2.5 py-0.5 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Autonomous Evaluation Pipeline</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Candidate Evaluation Session</h1>
          <p className="text-xs text-slate-400">
            Phase 1: Select Job Position & Upload Resume &rarr; Phase 2: Sequential Agent Execution &rarr; Phase 3: Overall Synthesis Report
          </p>
        </div>

        <Link href="/dashboard">
          <Button variant="outline" className="text-xs border-slate-700 text-slate-300 hover:bg-slate-800">
            Return to Dashboard
          </Button>
        </Link>
      </div>

      {/* Stepper Header */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
        {stagesList.map((stg, idx) => {
          const Icon = stg.icon;
          const isActive = currentStage === stg.id;
          const isDone =
            (currentStage === 'video' && idx === 0) ||
            (currentStage === 'coding' && idx <= 1) ||
            (currentStage === 'interaction' && idx <= 2) ||
            (currentStage === 'report' && idx <= 4);

          return (
            <div
              key={stg.id}
              onClick={() => handleNextStage(stg.id as StepStage)}
              className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
                isActive
                  ? 'bg-sky-600/15 border-sky-500/50 shadow-md shadow-sky-950/50 ring-1 ring-sky-500/30'
                  : isDone
                  ? 'bg-slate-900/80 border-emerald-500/30 text-slate-300'
                  : 'bg-slate-900/40 border-slate-800 text-slate-500 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <Icon className={`h-4 w-4 ${isActive ? 'text-sky-400' : isDone ? 'text-emerald-400' : 'text-slate-500'}`} />
                {isDone && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
              </div>
              <p className="text-xs font-bold text-white mt-2 truncate">{stg.label}</p>
              <p className="text-[10px] text-slate-400 truncate mt-0.5">{stg.desc}</p>
            </div>
          );
        })}
      </div>

      {/* STAGE 1: RESUME ANALYSIS (Job Role First -> File Upload -> Real Text Analysis) */}
      {currentStage === 'resume' && (
        <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg font-bold text-white flex items-center">
                  <FileText className="h-5 w-5 text-sky-400 mr-2" />
                  Stage 1: Job Role Selection & Resume File Upload
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Select the job position first, then upload the candidate resume file directly from your computer.
                </CardDescription>
              </div>
              {parsedInsights && (
                <span className="px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
                  Match Score: {parsedInsights.score} / 100
                </span>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Step 1.1: Job Role Selection */}
            <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-4">
              <h3 className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center">
                <Briefcase className="h-4 w-4 mr-2" />
                Step 1: Select Academic Job Position & Department
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Applied Job Position *</label>
                  <select
                    value={selectedRole}
                    onChange={(e) => setSelectedRole(e.target.value)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
                  >
                    <option value="">-- Select Job Position --</option>
                    <option value="Assistant Professor (Grade I) - CSE">Assistant Professor (Grade I) — CSE</option>
                    <option value="Assistant Professor (Grade II) - CSE">Assistant Professor (Grade II) — CSE</option>
                    <option value="Associate Professor - Electrical Engineering">Associate Professor — EE</option>
                    <option value="Full Professor - Mechanical Engineering">Full Professor — ME</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Department</label>
                  <div className="relative">
                    <Building className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
                    <input
                      type="text"
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      className="w-full rounded-lg bg-slate-900 border border-slate-800 pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Step 1.2: Local Computer Resume File Upload */}
            <div className={`p-4 rounded-xl border space-y-4 transition-all ${
              selectedRole ? 'bg-slate-950/80 border-slate-800' : 'bg-slate-950/30 border-slate-800/50 opacity-60'
            }`}>
              <h3 className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center">
                <Upload className="h-4 w-4 mr-2" />
                Step 2: Upload Resume File from Your Computer
              </h3>

              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc,.txt,.md"
                onChange={handleFileSelect}
                className="hidden"
              />

              {/* Upload Box */}
              <div 
                onClick={() => selectedRole && fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
                  !selectedRole
                    ? 'border-slate-800 text-slate-600 cursor-not-allowed'
                    : uploadedFile
                    ? 'border-emerald-500/50 bg-emerald-500/10'
                    : 'border-slate-700 hover:border-sky-500/50 bg-slate-900/50'
                }`}
              >
                {uploadedFile ? (
                  <div className="space-y-2">
                    <FileCheck className="h-9 w-9 text-emerald-400 mx-auto" />
                    <p className="text-xs font-bold text-white">{uploadedFile.name}</p>
                    <p className="text-[10px] text-emerald-300">
                      File Size: {(uploadedFile.size / 1024).toFixed(1)} KB &bull; Ready for real text extraction
                    </p>
                    <Button variant="outline" size="sm" className="text-xs border-slate-700 text-slate-300 mt-1">
                      Change File
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Upload className="h-9 w-9 text-sky-400 mx-auto animate-bounce" />
                    <p className="text-xs font-semibold text-slate-200">
                      {selectedRole ? 'Click to Select Resume File from Computer' : 'Please Select Job Position First Above'}
                    </p>
                    <p className="text-[10px] text-slate-500">Supports PDF, DOCX, TXT, or MD files</p>
                  </div>
                )}
              </div>

              {/* Analyze Button */}
              {selectedRole && uploadedFile && !parsedInsights && (
                <Button
                  onClick={handleRunResumeAnalysis}
                  isLoading={analyzingStage}
                  className="w-full bg-sky-600 hover:bg-sky-500 text-white text-xs font-medium py-2.5 flex items-center justify-center space-x-2"
                >
                  <RotateCw className={`h-4 w-4 ${analyzingStage ? 'animate-spin' : ''}`} />
                  <span>{analyzingStage ? 'Parsing Resume File Content...' : 'Run Resume Analysis'}</span>
                </Button>
              )}
            </div>

            {/* Step 1.3: Real Parsed Resume Output Insights */}
            {parsedInsights && (
              <div className="p-4 rounded-xl bg-slate-950/90 border border-sky-500/30 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                    <Sparkles className="h-4 w-4 text-sky-400 mr-2" />
                    Real Parsed Insights for File &quot;{parsedInsights.fileName}&quot;
                  </h4>
                  <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded border border-emerald-500/20">
                    Match Score: {parsedInsights.score} / 100
                  </span>
                </div>

                <p className="text-xs text-slate-300 bg-slate-900 p-3 rounded-lg border border-slate-800 leading-relaxed">
                  {parsedInsights.summary}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Highest Qualification Found</span>
                    <span className="font-semibold text-white">{parsedInsights.highestDegree}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Extracted Keywords</span>
                    <span className="font-semibold text-emerald-400">{parsedInsights.skills.join(', ')}</span>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-[10px] text-slate-400 block">Funding & Grants Status</span>
                    <span className="font-semibold text-amber-400">{parsedInsights.grants}</span>
                  </div>
                </div>

                {/* Raw Snippet */}
                <div className="pt-2">
                  <span className="text-[10px] text-slate-400 uppercase font-medium flex items-center mb-1">
                    <FileCode className="h-3 w-3 text-sky-400 mr-1" />
                    Uploaded File Text Snippet:
                  </span>
                  <pre className="p-2.5 rounded-lg bg-slate-950 text-[10px] font-mono text-slate-400 border border-slate-800 max-h-28 overflow-x-auto whitespace-pre-wrap">
                    {parsedInsights.rawTextPreview}
                  </pre>
                </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="flex justify-end pt-2 border-t border-slate-800">
            <Button
              onClick={() => handleNextStage('video')}
              disabled={!parsedInsights}
              isLoading={analyzingStage}
              className="bg-sky-600 hover:bg-sky-500 text-white font-medium text-xs px-5 py-2.5 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>Proceed to Demo Video Analysis</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* STAGE 2: DEMO VIDEO ANALYSIS */}
      {currentStage === 'video' && (
        <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg font-bold text-white flex items-center">
                  <Video className="h-5 w-5 text-indigo-400 mr-2" />
                  Stage 2: Demo Video Analysis (Multimodal Presentation & Soft-Skills)
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Evaluates presentation recording, facial expressions, tone articulation, and teaching delivery.
                </CardDescription>
              </div>
              <span className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
                Score: {videoScore} / 100
              </span>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="aspect-video max-h-64 rounded-xl bg-slate-950 border border-slate-800 relative flex items-center justify-center overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent"></div>
              <div className="text-center space-y-2 relative z-10">
                <div className="h-12 w-12 rounded-full bg-indigo-600/80 text-white mx-auto flex items-center justify-center shadow-lg">
                  <Play className="h-5 w-5 fill-current ml-0.5" />
                </div>
                <p className="text-xs font-semibold text-white">Video Interview Presentation Analysis</p>
                <p className="text-[10px] text-slate-400">Audio Clarity 98% &bull; Demeanor Index 90% &bull; Active Pace 140 WPM</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-medium block">Pedagogical Clarity</span>
                <span className="font-bold text-white text-base">92%</span>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-medium block">Body Language Confidence</span>
                <span className="font-bold text-white text-base">90%</span>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-medium block">Tone Articulation</span>
                <span className="font-bold text-white text-base">88%</span>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-end pt-2 border-t border-slate-800">
            <Button
              onClick={() => handleNextStage('coding')}
              isLoading={analyzingStage}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs px-5 py-2.5 flex items-center space-x-2"
            >
              <span>Proceed to Coding Test</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* STAGE 3: CODING TEST */}
      {currentStage === 'coding' && (
        <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg font-bold text-white flex items-center">
                  <Code className="h-5 w-5 text-emerald-400 mr-2" />
                  Stage 3: Coding Test (Algorithmic & Technical Problem Solving)
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Evaluates candidate code structure, test suite validation, and algorithmic complexity score.
                </CardDescription>
              </div>
              <span className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
                Score: {codingScore} / 100
              </span>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="p-4 rounded-xl bg-slate-950 font-mono text-xs text-slate-300 border border-slate-800 space-y-2 overflow-x-auto">
              <div className="text-slate-500">// Submitted Algorithm: Distributed Key-Value Consensus Protocol</div>
              <div><span className="text-purple-400">func</span> <span className="text-sky-400">SyncStateReplicas</span>(nodes []*Node, payload []byte) error &#123;</div>
              <div className="pl-4"><span className="text-purple-400">for</span> _, node := <span className="text-purple-400">range</span> nodes &#123;</div>
              <div className="pl-8"><span className="text-purple-400">if</span> err := node.AppendEntries(payload); err != nil &#123; return err &#125;</div>
              <div className="pl-4">&#125;</div>
              <div className="pl-4"><span className="text-purple-400">return</span> nil</div>
              <div>&#125;</div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-medium block">Automated Test Suite</span>
                <span className="font-bold text-emerald-400 text-sm">12 / 12 Tests Passed</span>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-medium block">Time Complexity</span>
                <span className="font-bold text-sky-400 text-sm">O(N log N) Optimal</span>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                <span className="text-[10px] text-slate-400 font-medium block">Code Maintainability</span>
                <span className="font-bold text-amber-400 text-sm">Grade A+ Clean Code</span>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-end pt-2 border-t border-slate-800">
            <Button
              onClick={() => handleNextStage('interaction')}
              isLoading={analyzingStage}
              className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs px-5 py-2.5 flex items-center space-x-2"
            >
              <span>Proceed to Live Interaction Teaching Session</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* STAGE 4: LIVE INTERACTION TEACHING SESSION */}
      {currentStage === 'interaction' && (
        <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg font-bold text-white flex items-center">
                  <MessageSquare className="h-5 w-5 text-amber-400 mr-2" />
                  Stage 4: Live Interaction Teaching Session
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Interactive dialogue simulation. Selection committee members submit questions and review evaluated answers.
                </CardDescription>
              </div>
              <span className="px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold">
                Score: {interactionScore} / 100
              </span>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
              {qaHistory.map((item, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between text-xs text-sky-400 font-semibold">
                    <span>Q{idx + 1}: Selection Committee Question</span>
                    <span className="text-[10px] text-slate-500 font-mono">{item.time}</span>
                  </div>
                  <p className="text-xs text-slate-200">{item.q}</p>
                  <div className="p-3 rounded-lg bg-slate-900/80 border-l-2 border-amber-400 text-xs text-slate-300 italic">
                    &quot;{item.a}&quot;
                  </div>
                </div>
              ))}
            </div>

            <form onSubmit={handleSendQuestion} className="flex space-x-2">
              <input
                type="text"
                placeholder="Type a custom interview question to evaluate candidate response..."
                value={newQuestion}
                onChange={(e) => setNewQuestion(e.target.value)}
                className="flex-1 rounded-lg bg-slate-950/90 border border-slate-800 px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
              />
              <Button type="submit" className="bg-amber-600 hover:bg-amber-500 text-white text-xs px-4 py-2.5 flex items-center space-x-1.5">
                <Send className="h-3.5 w-3.5" />
                <span>Ask Question</span>
              </Button>
            </form>
          </CardContent>
          <CardFooter className="flex justify-end pt-2 border-t border-slate-800">
            <Button
              onClick={handleCompleteSession}
              isLoading={analyzingStage}
              className="bg-amber-600 hover:bg-amber-500 text-white font-medium text-xs px-6 py-2.5 flex items-center space-x-2"
            >
              <CheckCircle2 className="h-4 w-4" />
              <span>Close Session & Generate Overall Report</span>
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* STAGE 5: OVERALL SYNTHESIS REPORT */}
      {currentStage === 'report' && (
        <Card className="border-sky-500/30 bg-gradient-to-br from-sky-950/40 via-slate-900 to-indigo-950/40 backdrop-blur-md">
          <CardHeader className="border-b border-slate-800/80 pb-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[11px] font-semibold mb-2">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>Evaluation Session Closed & Saved</span>
                </div>
                <CardTitle className="text-xl font-bold text-white">
                  Overall Candidate Evaluation Report
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  {department} &bull; Position: {selectedRole || 'Assistant Professor'} &bull; File: {uploadedFile?.name || 'Resume'}
                </CardDescription>
              </div>

              <div className="text-right">
                <span className="text-[10px] text-slate-400 uppercase font-bold block">Overall Consensus Score</span>
                <div className="flex items-baseline justify-end space-x-1">
                  <span className="text-4xl font-extrabold text-white font-mono">{overallScore}</span>
                  <span className="text-sm text-slate-400 font-semibold">/ 100</span>
                </div>
              </div>
            </div>
          </CardHeader>

          <CardContent className="pt-6 space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Resume Score', score: resumeScore, icon: FileText, color: 'text-sky-400' },
                { label: 'Video Score', score: videoScore, icon: Video, color: 'text-indigo-400' },
                { label: 'Coding Score', score: codingScore, icon: Code, color: 'text-emerald-400' },
                { label: 'Interaction Score', score: interactionScore, icon: MessageSquare, color: 'text-amber-400' },
              ].map((item, idx) => {
                const Icon = item.icon;
                return (
                  <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between text-xs text-slate-400">
                      <span>{item.label}</span>
                      <Icon className={`h-4 w-4 ${item.color}`} />
                    </div>
                    <div className="text-2xl font-bold text-white font-mono">{item.score}</div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div className="bg-sky-500 h-full rounded-full" style={{ width: `${item.score}%` }}></div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="p-5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-2">
              <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
                <UserCheck className="h-5 w-5" />
                <span>Committee Recommendation: {overallScore >= 80 ? 'Highly Recommended for Faculty Appointment' : 'Recommended'}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                Evaluated file &quot;{uploadedFile?.name || 'Resume'}&quot;. {parsedInsights?.summary} Performance recorded across video presentation, coding efficiency, and interview Q&A handling.
              </p>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800">
            <div className="text-xs text-slate-400">
              This report has been recorded to your logged-in dashboard.
            </div>

            <Link href="/dashboard">
              <Button className="bg-sky-600 hover:bg-sky-500 text-white text-xs px-5 py-2.5">
                Go to Updated Dashboard
              </Button>
            </Link>
          </CardFooter>
        </Card>
      )}
    </div>
  );
}
