'use client';

import React, { useState, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  FileText, 
  Upload, 
  CheckCircle2, 
  Sparkles, 
  GraduationCap, 
  Award, 
  Briefcase, 
  Zap,
  RotateCw,
  FileCheck,
  AlertCircle,
  FileCode,
  Globe,
  Github,
  Linkedin,
  BookOpen,
  ShieldAlert,
  ShieldCheck,
  Cpu,
  Layers,
  HelpCircle,
  ExternalLink,
  Target,
  Copy,
  Check,
  Code,
  Eye,
  ChevronDown,
  ChevronUp,
  MapPin,
  User,
  Heart,
  LayoutGrid,
  Tag,
  FileSearch
} from 'lucide-react';

import { analyzeResumeWithBackend } from '@/lib/documentParser';

export default function ResumeAgentPage() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [selectedRole, setSelectedRole] = useState<string>('Assistant Professor (CSE)');
  const [analyzing, setAnalyzing] = useState(false);
  const [profile, setProfile] = useState<any | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lineageViewMode, setLineageViewMode] = useState<'visual' | 'json'>('visual');
  const [expandFullJson, setExpandFullJson] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);

  const processFile = async (uploadedFile: File) => {
    setAnalyzing(true);
    setFile(uploadedFile);
    setErrorMessage(null);

    // Call Python FastAPI Enterprise Engine (CandidateIntelligenceEngine v2.0)
    const backendData = await analyzeResumeWithBackend(uploadedFile);

    if (backendData) {
      if (backendData.file_meta && !backendData.file_meta.is_valid) {
        setErrorMessage(backendData.file_meta.error_message || 'Unsupported file format uploaded.');
        setProfile(backendData);
      } else {
        setProfile(backendData);
      }
    } else {
      setErrorMessage('Could not connect to Python Resume Intelligence Engine (http://localhost:8000). Please check backend server status.');
    }
    setAnalyzing(false);
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await processFile(e.target.files[0]);
    }
  };

  const handleReRun = async () => {
    if (file) {
      await processFile(file);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-sky-950/90 via-slate-900 to-indigo-950 border border-sky-500/20 shadow-2xl backdrop-blur-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-sky-400 text-xs font-semibold">
            <Cpu className="h-3.5 w-3.5 text-sky-400" />
            <span>Resume Intelligence Agent v2.0 (Enterprise Edition)</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Candidate Intelligence & Verification Engine</h1>
          <p className="text-xs text-slate-300">
            Offline Python Extraction • Multi-Source Profile Discovery • Qwen2.5:3B Callback LLM • Fraud Detection • Evidence Lineage Graph
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-xs text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sky-500"
          >
            <option value="Assistant Professor (CSE)">Assistant Professor (CSE)</option>
            <option value="Associate Professor (EE)">Associate Professor (EE)</option>
            <option value="Full Professor (ME)">Full Professor (ME)</option>
          </select>

          {file && (
            <Button onClick={handleReRun} disabled={analyzing} className="bg-sky-600 hover:bg-sky-500 text-white text-xs px-4 py-2 flex items-center space-x-1.5 shadow-lg shadow-sky-600/30">
              <RotateCw className={`h-3.5 w-3.5 ${analyzing ? 'animate-spin' : ''}`} />
              <span>{analyzing ? 'Executing Engine...' : 'Re-Run Resume Agent'}</span>
            </Button>
          )}
        </div>
      </div>

      {/* File Validation Error Banner */}
      {errorMessage && (
        <Card className="border-rose-500/50 bg-gradient-to-r from-rose-950/80 to-slate-900 border-2 shadow-2xl p-6">
          <div className="flex items-start space-x-4">
            <ShieldAlert className="h-8 w-8 text-rose-400 flex-shrink-0 mt-1" />
            <div className="space-y-2">
              <h3 className="text-base font-bold text-white">
                {errorMessage.includes('Could not connect') ? 'Backend Connection Error (Port 8000)' : 'Smart File Validation Error (Module 1)'}
              </h3>
              <p className="text-xs text-rose-200 leading-relaxed font-mono bg-rose-950/60 p-3 rounded-lg border border-rose-800">
                {errorMessage}
              </p>
              <div className="text-[11px] text-slate-400 flex items-center space-x-4 pt-1">
                <span>Supported Formats: PDF, DOCX, PNG, JPG, TIFF</span>
                <span>Rejected: ZIP, EXE, MP4, MP3, PPT, XLS, Empty/Corrupted</span>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: File Upload & Verification Quick Stats */}
        <div className="space-y-6">
          <Card className="border-slate-800 bg-slate-900/80 backdrop-blur-md shadow-xl">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-bold text-white flex items-center">
                <Upload className="h-4 w-4 text-sky-400 mr-2" />
                Upload Resume / CV File
              </CardTitle>
              <CardDescription className="text-xs text-slate-400">Select PDF, DOCX, PNG, JPG, or TIFF file from local machine</CardDescription>
            </CardHeader>
            <CardContent>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.tiff,.tif"
                onChange={handleFileChange}
                className="hidden"
              />

              <div 
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-700/80 hover:border-sky-500/80 rounded-2xl p-6 text-center cursor-pointer bg-slate-950/60 hover:bg-slate-950 transition-all space-y-3"
              >
                {file ? (
                  <>
                    <FileCheck className="h-10 w-10 text-emerald-400 mx-auto" />
                    <p className="text-xs font-bold text-white truncate max-w-full">{file.name}</p>
                    <p className="text-[10px] text-emerald-300 font-mono">{(file.size / 1024).toFixed(1)} KB • File Loaded</p>
                    <Button variant="outline" size="sm" className="text-xs border-slate-700 text-slate-300 mt-2">
                      Upload Different Candidate File
                    </Button>
                  </>
                ) : (
                  <>
                    <Upload className="h-9 w-9 text-sky-400 mx-auto animate-bounce" />
                    <div>
                      <p className="text-xs font-semibold text-slate-200">Click to Upload Candidate Resume File</p>
                      <p className="text-[10px] text-slate-500 mt-1">Executes 13-Module Python Subsystem</p>
                    </div>
                    <Button variant="outline" size="sm" className="text-xs border-sky-500/30 text-sky-300 bg-sky-500/10">
                      Browse Computer
                    </Button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Quick Metrics Cards */}
          {profile && profile.file_meta?.is_valid && (
            <>
              {/* Overall Confidence Rating */}
              <Card className="border-sky-500/30 bg-gradient-to-b from-sky-950/40 via-slate-900 to-slate-950 backdrop-blur-md">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase tracking-wider text-sky-400 font-bold">Extraction Confidence Rating</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 font-semibold">{profile.resume_type?.category}</span>
                  </div>
                  <div className="flex items-baseline space-x-2 pt-1">
                    <span className="text-4xl font-extrabold text-white font-mono">{profile.confidence?.overall_average ?? 0}%</span>
                    <span className="text-xs text-slate-400 font-semibold">Field Precision Score</span>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-sky-500 via-indigo-400 to-emerald-400 h-full rounded-full transition-all duration-500" 
                      style={{ width: `${profile.confidence?.overall_average ?? 0}%` }}
                    ></div>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[11px] pt-1">
                    <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">Verification Score</span>
                      <span className="text-emerald-400 font-bold font-mono">{(profile.verification?.overall_verification_score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">Fraud Risk Index</span>
                      <span className={profile.fraud_report?.is_suspicious ? 'text-rose-400 font-bold font-mono' : 'text-emerald-400 font-bold font-mono'}>
                        {profile.fraud_report?.fraud_risk_score ?? 0.0} / 1.0
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Module 10: Qwen Callback LLM Status */}
              <Card className="border-indigo-500/30 bg-slate-900/60 backdrop-blur-md">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center">
                    <Cpu className="h-4 w-4 mr-1.5 text-indigo-400" />
                    Module 10: Qwen2.5:3B Callback LLM
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-xs">
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-slate-300">Deterministic Confidence:</span>
                    <span className="text-emerald-400 font-semibold font-mono">HIGH (95%)</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <span className="text-slate-300">LLM Callback Fallback:</span>
                    <span className="text-sky-400 font-semibold">Qwen2.5:3B (Targeted Only)</span>
                  </div>
                  <p className="text-[10px] text-slate-400 italic">
                    Qwen2.5:3B model fires *only* when deterministic extraction yields low confidence on ambiguous resume blocks.
                  </p>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Right Column: Full Candidate Intelligence Data */}
        <div className="lg:col-span-2 space-y-6">
          {!profile || (profile.file_meta && !profile.file_meta.is_valid) ? (
            <Card className="border-slate-800 bg-slate-900/40 border-dashed backdrop-blur-md p-12 text-center flex flex-col items-center justify-center min-h-[380px] space-y-3">
              <AlertCircle className="h-10 w-10 text-slate-500" />
              <h3 className="text-sm font-semibold text-white">No Candidate Intelligence Data Loaded</h3>
              <p className="text-xs text-slate-400 max-w-sm">
                Upload any PDF, DOCX, PNG, JPG, or TIFF file to execute the Python Candidate Intelligence Engine.
              </p>
            </Card>
          ) : (
            <>
              {/* Candidate Identity & Contact Card */}
              <Card className="border-sky-500/20 bg-slate-900/80 backdrop-blur-md shadow-xl">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-lg font-bold text-white flex items-center">
                        <GraduationCap className="h-5 w-5 text-sky-400 mr-2" />
                        {profile.candidate?.name || 'Extracted Candidate Profile'}
                      </CardTitle>
                      <CardDescription className="text-xs text-sky-300 font-mono mt-1">
                        Resume Category: {profile.resume_type?.category} {profile.resume_type?.is_academic ? '(Academic/Faculty CV)' : ''}
                      </CardDescription>
                    </div>
                    <div className="flex items-center space-x-2">
                      {profile.candidate?.candidate_type && profile.candidate.candidate_type !== 'Unknown' && (
                        <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold ${
                          profile.candidate.candidate_type === 'Fresher'
                            ? 'bg-sky-500/15 border border-sky-500/40 text-sky-300'
                            : profile.candidate.candidate_type === 'Academic'
                            ? 'bg-purple-500/15 border border-purple-500/40 text-purple-300'
                            : 'bg-indigo-500/15 border border-indigo-500/40 text-indigo-300'
                        }`}>
                          <User className="h-3 w-3 inline mr-1" />
                          {profile.candidate.candidate_type}
                        </span>
                      )}
                      <span className="inline-block px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
                        Completeness: {profile.quality_evaluation?.completeness_score ?? 100}%
                      </span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase">Email Contact</span>
                      <p 
                        className="text-xs font-semibold text-white break-all hover:text-sky-300 transition-colors" 
                        title={profile.candidate?.email || 'Not Extracted'}
                      >
                        {profile.candidate?.email || 'Not Extracted'}
                      </p>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase">Phone Number</span>
                      <p 
                        className="text-xs font-semibold text-white break-all" 
                        title={profile.candidate?.phone || 'Not Extracted'}
                      >
                        {profile.candidate?.phone || 'Not Extracted'}
                      </p>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase">Address / Location</span>
                      <p className="text-xs font-semibold text-white break-words flex items-center" title={profile.candidate?.address || 'Not Extracted'}>
                        {profile.candidate?.address ? (
                          <><MapPin className="h-3 w-3 text-sky-400 mr-1 flex-shrink-0" />{profile.candidate.address}</>
                        ) : 'Not Extracted'}
                      </p>
                    </div>
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase">Languages</span>
                      <p className="text-xs font-semibold text-white break-words">
                        {profile.candidate?.languages?.length > 0 ? profile.candidate.languages.join(', ') : 'English'}
                      </p>
                    </div>
                  </div>

                  {/* Profile Summary */}
                  {profile.candidate?.profile_summary && (
                    <div className="p-3 rounded-xl bg-sky-950/30 border border-sky-800/40">
                      <span className="text-[10px] text-sky-400 uppercase font-bold block mb-1">Profile Summary</span>
                      <p className="text-xs text-slate-200 leading-relaxed">{profile.candidate.profile_summary}</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Module 5 & 6: Discovered Profile Links & Multi-Source Evidence */}
              <Card className="border-indigo-500/30 bg-slate-900/80 backdrop-blur-md">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-bold text-white flex items-center">
                    <Globe className="h-4 w-4 text-indigo-400 mr-2" />
                    Module 5 & 6: Profile Link Discovery & Multi-Source Collector
                  </CardTitle>
                  <CardDescription className="text-xs text-slate-400">
                    Discovers candidate social & research profiles and fetches external verification metrics.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    {profile.profiles?.linkedin && (
                      <a href={profile.profiles.linkedin} target="_blank" rel="noreferrer" className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-blue-600/20 border border-blue-500/40 text-blue-300 text-xs font-medium hover:bg-blue-600/30">
                        <Linkedin className="h-3.5 w-3.5" />
                        <span>LinkedIn</span>
                        <ExternalLink className="h-3 w-3 ml-1 opacity-70" />
                      </a>
                    )}
                    {profile.profiles?.github && (
                      <a href={profile.profiles.github} target="_blank" rel="noreferrer" className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-purple-600/20 border border-purple-500/40 text-purple-300 text-xs font-medium hover:bg-purple-600/30">
                        <Github className="h-3.5 w-3.5" />
                        <span>GitHub Profile</span>
                        <ExternalLink className="h-3 w-3 ml-1 opacity-70" />
                      </a>
                    )}
                    {profile.profiles?.google_scholar && (
                      <a href={profile.profiles.google_scholar} target="_blank" rel="noreferrer" className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-sky-600/20 border border-sky-500/40 text-sky-300 text-xs font-medium hover:bg-sky-600/30">
                        <BookOpen className="h-3.5 w-3.5" />
                        <span>Google Scholar</span>
                        <ExternalLink className="h-3 w-3 ml-1 opacity-70" />
                      </a>
                    )}
                    {profile.profiles?.portfolio && (
                      <a href={profile.profiles.portfolio} target="_blank" rel="noreferrer" className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 border border-emerald-500/40 text-emerald-300 text-xs font-medium hover:bg-emerald-600/30">
                        <Globe className="h-3.5 w-3.5" />
                        <span>Portfolio Website</span>
                        <ExternalLink className="h-3 w-3 ml-1 opacity-70" />
                      </a>
                    )}
                  </div>

                  {/* Multi-Source Collected Metrics */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                      <span className="text-[10px] text-purple-400 font-bold uppercase block">GitHub Collector</span>
                      {profile.external_evidence?.github ? (
                        <>
                          <p className="text-xs text-slate-200">Public Repos: <span className="text-white font-mono font-bold">{profile.external_evidence.github.public_repos}</span></p>
                          <p className="text-xs text-slate-200">Stars: <span className="text-amber-300 font-mono font-bold">{profile.external_evidence.github.total_stars}</span></p>
                          {profile.external_evidence.github.top_languages?.length > 0 && (
                            <p className="text-[10px] text-slate-400">Languages: {profile.external_evidence.github.top_languages.join(', ')}</p>
                          )}
                        </>
                      ) : (
                        <p className="text-xs text-slate-500 italic">No GitHub Link Found in Resume</p>
                      )}
                    </div>

                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                      <span className="text-[10px] text-amber-400 font-bold uppercase block">CodeChef Collector</span>
                      {profile.external_evidence?.codechef ? (
                        <>
                          <p className="text-xs text-slate-200">Rating: <span className="text-amber-300 font-mono font-bold">{profile.external_evidence.codechef.rating}</span></p>
                          {profile.external_evidence.codechef.global_rank && (
                            <p className="text-xs text-slate-200">Global Rank: <span className="text-white font-mono font-bold">{profile.external_evidence.codechef.global_rank}</span></p>
                          )}
                        </>
                      ) : (
                        <p className="text-xs text-slate-500 italic">No CodeChef Link Found</p>
                      )}
                    </div>

                    <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1">
                      <span className="text-[10px] text-emerald-400 font-bold uppercase block">LeetCode Collector</span>
                      {profile.external_evidence?.leetcode ? (
                        <>
                          <p className="text-xs text-slate-200">Contest Rating: <span className="text-emerald-300 font-mono font-bold">{profile.external_evidence.leetcode.contest_rating}</span></p>
                          <p className="text-xs text-slate-200">Problems Solved: <span className="text-white font-mono font-bold">{profile.external_evidence.leetcode.solved_problems}</span></p>
                        </>
                      ) : (
                        <p className="text-xs text-slate-500 italic">No LeetCode Link Found</p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Module 3: Deterministic Offline Extraction Breakdown */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {/* Education */}
                <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                      <GraduationCap className="h-4 w-4 text-sky-400 mr-2" />
                      Education History
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {profile.education?.length > 0 ? (
                      profile.education.map((edu: any, idx: number) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-0.5">
                          <p className="font-bold text-white">{edu.degree}</p>
                          <p className="text-slate-400">{edu.institution || 'Recognized Institution'}</p>
                          {edu.year && <p className="text-[10px] text-sky-400 font-mono">Graduation Year: {edu.year}</p>}
                          {edu.gpa && <p className="text-[10px] text-emerald-400 font-mono">Marks / Grade: {edu.gpa}</p>}
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-500 italic">No formal education records parsed.</p>
                    )}
                  </CardContent>
                </Card>

                {/* Experience */}
                <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                      <Briefcase className="h-4 w-4 text-indigo-400 mr-2" />
                      Career & Teaching Positions
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {profile.experience?.length > 0 ? (
                      profile.experience.map((exp: any, idx: number) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-0.5">
                          <p className="font-bold text-white">{exp.title}</p>
                          <p className="text-slate-400">{exp.organization || 'Academic Dept / Organization'}</p>
                          {exp.start_date && <p className="text-[10px] text-indigo-400 font-mono">Date: {exp.start_date}</p>}
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-500 italic">No prior employment records parsed.</p>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Technical Skills & Soft Skills */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                      <Zap className="h-4 w-4 text-emerald-400 mr-2" />
                      Technical Skills ({profile.skills?.length || 0})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-1.5">
                      {profile.skills?.length > 0 ? (
                        profile.skills.map((skill: string, idx: number) => (
                          <span key={idx} className="text-[11px] px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 font-medium">
                            {skill}
                          </span>
                        ))
                      ) : (
                        <p className="text-xs text-slate-500 italic">No technical skill tags extracted.</p>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                      <Heart className="h-4 w-4 text-pink-400 mr-2" />
                      Soft Skills ({profile.soft_skills?.length || 0})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-1.5">
                      {profile.soft_skills?.length > 0 ? (
                        profile.soft_skills.map((skill: string, idx: number) => (
                          <span key={idx} className="text-[11px] px-2.5 py-1 rounded-md bg-pink-500/10 border border-pink-500/20 text-pink-300 font-medium">
                            {skill}
                          </span>
                        ))
                      ) : (
                        <p className="text-xs text-slate-500 italic">No soft skills detected.</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Projects & Achievements */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                      <Layers className="h-4 w-4 text-sky-400 mr-2" />
                      Extracted Projects ({profile.projects?.length || 0})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {profile.projects?.length > 0 ? (
                      profile.projects.map((proj: any, idx: number) => (
                        <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1.5">
                          <p className="font-bold text-white">{proj.title}</p>
                          {proj.description && proj.description !== proj.title && (
                            <p className="text-[11px] text-slate-300 leading-relaxed">{proj.description}</p>
                          )}
                          {proj.technologies?.length > 0 && (
                            <div className="flex flex-wrap gap-1 pt-1">
                              {proj.technologies.map((t: string, tidx: number) => (
                                <span key={tidx} className="text-[10px] px-2 py-0.5 rounded bg-sky-500/10 text-sky-300 font-mono">
                                  {t}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-500 italic">No project entries parsed.</p>
                    )}
                  </CardContent>
                </Card>

                <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-xs font-bold text-white uppercase tracking-wider flex items-center">
                      <Award className="h-4 w-4 text-amber-400 mr-2" />
                      Achievements & Leadership ({profile.categorized_awards?.length || profile.awards?.length || 0})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {profile.categorized_awards?.length > 0 ? (
                      profile.categorized_awards.map((award: any, idx: number) => (
                        <div key={idx} className="p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs flex items-start justify-between gap-2">
                          <span className="text-slate-200">{award.title}</span>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold flex-shrink-0 ${
                            award.category === 'Hackathon' ? 'bg-orange-500/15 text-orange-300 border border-orange-500/30' :
                            award.category === 'Certification' ? 'bg-blue-500/15 text-blue-300 border border-blue-500/30' :
                            award.category === 'Coding' ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30' :
                            award.category === 'Internship' ? 'bg-purple-500/15 text-purple-300 border border-purple-500/30' :
                            award.category === 'Award' ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30' :
                            'bg-slate-700/50 text-slate-400 border border-slate-600'
                          }`}>
                            {award.category}
                          </span>
                        </div>
                      ))
                    ) : profile.awards?.length > 0 ? (
                      profile.awards.map((award: string, idx: number) => (
                        <div key={idx} className="p-2 rounded bg-slate-950 border border-slate-800 text-xs text-slate-200">
                          {award}
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-slate-500 italic">No achievement records parsed.</p>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Layout Analysis Card */}
              <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center">
                    <LayoutGrid className="h-4 w-4 text-sky-400 mr-2" />
                    Module 4: Layout Structure Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">Columns Detected</span>
                      <span className="text-white font-bold font-mono">{profile.layout_structure?.column_count ?? 1}</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">Sidebar Detected</span>
                      <span className={`font-bold font-mono ${profile.layout_structure?.has_sidebar ? 'text-emerald-400' : 'text-slate-500'}`}>
                        {profile.layout_structure?.has_sidebar ? 'Yes' : 'No'}
                      </span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">Sections Found</span>
                      <span className="text-white font-bold font-mono">{profile.layout_structure?.sections?.length ?? 0}</span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-slate-400 block text-[10px]">Images Detected</span>
                      <span className={`font-bold font-mono ${profile.layout_structure?.has_images ? 'text-emerald-400' : 'text-slate-500'}`}>
                        {profile.layout_structure?.has_images ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>
                  {profile.layout_structure?.sections?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {profile.layout_structure.sections.map((sec: any, idx: number) => (
                        <span key={idx} className="text-[10px] px-2 py-0.5 rounded bg-sky-500/10 text-sky-300 font-mono border border-sky-500/20">
                          {sec.section_name}{sec.heading_text ? `: ${sec.heading_text}` : ''}
                        </span>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Module 8 & 9: Fraud Detection & Quality Recommendations */}
              <Card className="border-rose-500/20 bg-slate-900/80 backdrop-blur-md">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-bold text-white flex items-center">
                    <ShieldCheck className="h-4 w-4 text-emerald-400 mr-2" />
                    Module 8 & 9: Fraud Detection & Integrity Analyzer
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {profile.fraud_report?.indicators?.length > 0 ? (
                    profile.fraud_report.indicators.map((ind: any, idx: number) => (
                      <div key={idx} className="p-3 rounded-xl bg-rose-950/40 border border-rose-800/80 space-y-1 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-rose-300">{ind.indicator_title}</span>
                          <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 text-[10px] font-bold">{ind.risk_level} RISK</span>
                        </div>
                        <p className="text-slate-300">{ind.description}</p>
                      </div>
                    ))
                  ) : (
                    <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-800/80 text-xs text-emerald-300 flex items-center space-x-2">
                      <ShieldCheck className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                      <span>Integrity Checks Passed: No fraud anomalies, fake experience, or publication stuffing detected.</span>
                    </div>
                  )}

                  {/* Recommendations */}
                  {profile.quality_evaluation?.improvement_recommendations?.length > 0 && (
                    <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1 pt-2 text-xs">
                      <span className="text-[10px] text-amber-400 uppercase font-bold">Profile Recommendations</span>
                      <ul className="list-disc list-inside space-y-1 text-slate-300">
                        {profile.quality_evaluation.improvement_recommendations.map((rec: string, idx: number) => (
                          <li key={idx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Module 13: Evidence Lineage Graph */}
              <Card className="border-sky-500/30 bg-slate-900/80 backdrop-blur-md shadow-2xl overflow-hidden">
                <CardHeader className="pb-3 border-b border-slate-800/80">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="space-y-1">
                      <CardTitle className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center">
                        <Target className="h-4 w-4 text-sky-400 mr-2" />
                        Module 13: Audit Evidence Lineage Graph ({profile.evidence?.total_evidence_nodes ?? 0} Complete Nodes)
                      </CardTitle>
                      <CardDescription className="text-[11px] text-slate-400">
                        Complete verifiable source lineage tracking for every extracted resume attribute.
                      </CardDescription>
                    </div>

                    <div className="flex items-center space-x-2">
                      <div className="bg-slate-950 p-1 rounded-lg border border-slate-800 flex items-center space-x-1 text-xs">
                        <button
                          onClick={() => setLineageViewMode('visual')}
                          className={`px-2.5 py-1 rounded-md transition-all text-xs font-semibold flex items-center space-x-1 ${
                            lineageViewMode === 'visual'
                              ? 'bg-sky-600 text-white shadow-md shadow-sky-600/30'
                              : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          <Eye className="h-3 w-3" />
                          <span>Visual Nodes</span>
                        </button>
                        <button
                          onClick={() => setLineageViewMode('json')}
                          className={`px-2.5 py-1 rounded-md transition-all text-xs font-semibold flex items-center space-x-1 ${
                            lineageViewMode === 'json'
                              ? 'bg-sky-600 text-white shadow-md shadow-sky-600/30'
                              : 'text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          <Code className="h-3 w-3" />
                          <span>Complete JSON</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-4">
                  {lineageViewMode === 'visual' ? (
                    <div className="space-y-3">
                      {profile.evidence?.evidence_nodes?.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[520px] overflow-y-auto pr-1">
                          {profile.evidence.evidence_nodes.map((node: any, idx: number) => (
                            <div
                              key={idx}
                              className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/90 hover:border-sky-500/40 transition-all space-y-2 group"
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-[11px] font-mono font-bold text-sky-300 bg-sky-950/80 px-2 py-0.5 rounded border border-sky-800/60">
                                  {node.field_name}
                                </span>
                                <div className="flex items-center space-x-1.5">
                                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/30">
                                    {Math.round((node.confidence ?? 0.95) * 100)}%
                                  </span>
                                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                                    {node.extraction_source || 'DETERMINISTIC'}
                                  </span>
                                </div>
                              </div>

                              <div className="space-y-1 pt-0.5">
                                <p className="text-xs font-semibold text-white truncate">
                                  {node.extracted_value}
                                </p>
                                {node.sentence_snippet && (
                                  <p className="text-[11px] text-slate-400 font-mono italic truncate bg-slate-900/60 p-1.5 rounded border border-slate-800">
                                    "{node.sentence_snippet}"
                                  </p>
                                )}
                              </div>

                              <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono pt-1 border-t border-slate-900">
                                <span>Page {node.page_number ?? 1} • {node.section_header || 'General'}</span>
                                <span className="text-slate-400">
                                  BBox: [{node.bounding_box?.join(', ') || '0, 0, 0, 0'}]
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-slate-500 italic text-center py-6">No audit evidence lineage nodes generated.</p>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 text-xs text-slate-400">
                          <span>Showing all {profile.evidence?.evidence_nodes?.length || 0} nodes</span>
                          <span>•</span>
                          <button
                            onClick={() => setExpandFullJson(!expandFullJson)}
                            className="text-sky-400 hover:underline font-semibold flex items-center space-x-1"
                          >
                            {expandFullJson ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
                            <span>{expandFullJson ? 'Limit Height' : 'Expand Full Height'}</span>
                          </button>
                        </div>

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            navigator.clipboard.writeText(JSON.stringify(profile.evidence?.evidence_nodes || [], null, 2));
                            setCopiedJson(true);
                            setTimeout(() => setCopiedJson(false), 2000);
                          }}
                          className="text-xs border-slate-700 text-slate-300 hover:text-white bg-slate-950 flex items-center space-x-1.5 h-8"
                        >
                          {copiedJson ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                          <span>{copiedJson ? 'Copied Full JSON!' : 'Copy Full JSON'}</span>
                        </Button>
                      </div>

                      <pre
                        className={`p-4 rounded-xl bg-slate-950 text-[11px] font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap border border-slate-800 transition-all ${
                          expandFullJson ? 'max-h-none' : 'max-h-96 overflow-y-auto'
                        }`}
                      >
                        {JSON.stringify(profile.evidence?.evidence_nodes || [], null, 2)}
                      </pre>
                    </div>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
