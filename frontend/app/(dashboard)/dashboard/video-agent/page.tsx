'use client';

import React, { useState, useRef } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { 
  Video, 
  Play, 
  Sparkles, 
  Volume2, 
  CheckCircle2, 
  RotateCw,
  Clock,
  Upload,
  AlertCircle,
  FileVideo,
  Award,
  Layers,
  Eye,
  Activity,
  Check,
  Zap,
  BarChart3
} from 'lucide-react';

interface EvaluationReport {
  job_id: string;
  overall_score: number;
  scores: {
    clarity_and_delivery: number;
    visual_and_engagement: number;
    content_and_pedagogy: number;
    overall_score: number;
  };
  recommendation: {
    recommendation: string;
    confidence_level: number;
    summary: str;
  };
  strengths: string[];
  weaknesses: string[];
  html_report_path: string;
  md_report_path: string;
  json_report_path: string;
}

export default function VideoAgentPage() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'metrics' | 'report'>('metrics');

  const processVideoFile = async (uploadedFile: File) => {
    setAnalyzing(true);
    setFile(uploadedFile);
    setErrorMessage(null);
    setReport(null);

    // Create local object URL for instant video player preview
    const previewUrl = URL.createObjectURL(uploadedFile);
    setVideoPreviewUrl(previewUrl);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const res = await fetch('http://localhost:8005/video/evaluate', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || errData.message || `Evaluation failed with status ${res.status}`);
      }

      const reportData: EvaluationReport = await res.json();
      setReport(reportData);
    } catch (err: any) {
      console.error('Video evaluation failed:', err);
      setErrorMessage(err.message || 'Could not connect to Video Evaluation Agent (http://localhost:8005). Please verify backend status.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await processVideoFile(e.target.files[0]);
    }
  };

  const handleDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processVideoFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  return (
    <div className="space-y-8 max-w-7xl">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-indigo-950/90 via-slate-900 to-indigo-950 border border-indigo-500/20 shadow-2xl backdrop-blur-xl">
        <div className="space-y-1">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold">
            <Video className="h-3.5 w-3.5 text-indigo-400" />
            <span>Multimodal Video Evaluation Agent (Phases 1–9)</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Teaching Demonstration & Video Evaluation Engine</h1>
          <p className="text-xs text-slate-300">
            Offline-first AI Agent evaluating speech delivery, slide OCR, MediaPipe gestures, and teaching intelligence.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="video/mp4,video/mov,video/avi,video/mkv,video/webm"
            className="hidden"
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={analyzing}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs px-5 py-2.5 rounded-xl shadow-lg flex items-center space-x-2 transition-all"
          >
            <Upload className="h-4 w-4" />
            <span>{analyzing ? 'Evaluating Video...' : 'Upload Video File'}</span>
          </Button>
        </div>
      </div>

      {/* Video Upload Dropzone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
        className="group relative cursor-pointer rounded-2xl border-2 border-dashed border-indigo-500/30 hover:border-indigo-500/60 bg-gradient-to-b from-indigo-950/20 via-slate-900/60 to-slate-950/80 p-8 text-center transition-all shadow-xl hover:shadow-indigo-500/10"
      >
        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="h-16 w-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
            {analyzing ? (
              <RotateCw className="h-8 w-8 animate-spin text-indigo-400" />
            ) : (
              <FileVideo className="h-8 w-8" />
            )}
          </div>

          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">
              {file ? file.name : 'Drag & drop demo teaching video here, or click to browse'}
            </h3>
            <p className="text-xs text-slate-400">
              Supported Formats: MP4, MOV, AVI, MKV, WEBM (Max 500MB, 10s minimum)
            </p>
          </div>

          {file && (
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-lg bg-indigo-500/20 text-indigo-300 text-xs font-semibold">
              <Check className="h-3.5 w-3.5" />
              <span>Selected: {file.name} ({(file.size / (1024 * 1024)).toFixed(1)} MB)</span>
            </div>
          )}
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-red-950/60 border border-red-500/30 text-red-300 text-xs flex items-start space-x-3 shadow-lg">
          <AlertCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">Evaluation Error</span>
            <p>{errorMessage}</p>
          </div>
        </div>
      )}

      {/* Main Grid: Video Player & Results */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Video Player */}
        <div className="space-y-6">
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md overflow-hidden shadow-2xl">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-bold text-white flex items-center">
                <Video className="h-4 w-4 text-indigo-400 mr-2" />
                Teaching Video Stream
              </CardTitle>
            </CardHeader>
            <CardContent className="p-4 space-y-3">
              {videoPreviewUrl ? (
                <video
                  src={videoPreviewUrl}
                  controls
                  className="w-full aspect-video rounded-xl bg-black border border-slate-800"
                />
              ) : (
                <div className="aspect-video bg-slate-950 rounded-xl border border-slate-800/80 flex flex-col items-center justify-center text-slate-500 text-xs space-y-2">
                  <Play className="h-8 w-8 text-slate-600" />
                  <span>Upload a video to preview player</span>
                </div>
              )}

              {file && (
                <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/80">
                  <span className="flex items-center"><Volume2 className="h-3.5 w-3.5 text-indigo-400 mr-1" /> Audio Track Active</span>
                  <span className="flex items-center"><Clock className="h-3.5 w-3.5 text-sky-400 mr-1" /> Ready for AI Analysis</span>
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Score Index Card */}
          <Card className="border-indigo-500/30 bg-gradient-to-b from-indigo-950/40 via-slate-900/60 to-slate-950/90 backdrop-blur-md shadow-2xl">
            <CardHeader className="pb-2">
              <span className="text-[10px] uppercase tracking-wider text-indigo-400 font-bold flex items-center">
                <Award className="h-3.5 w-3.5 mr-1" /> Composite Teaching Score
              </span>
              <div className="flex items-baseline space-x-2">
                <span className="text-4xl font-extrabold text-white font-mono">
                  {report ? report.overall_score : '--'}
                </span>
                <span className="text-sm text-slate-400 font-semibold">/ 100</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 via-sky-400 to-emerald-400 h-full rounded-full transition-all duration-700"
                  style={{ width: `${report ? report.overall_score : 0}%` }}
                ></div>
              </div>

              {report && (
                <div className="pt-2 flex items-center justify-between">
                  <span className="text-xs text-slate-300 font-semibold">Recommendation:</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    report.recommendation.recommendation === 'Recommend'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  }`}>
                    {report.recommendation.recommendation}
                  </span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Detailed 9-Phase Evaluation Diagnostics */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-2xl">
            <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-slate-800/80">
              <div>
                <CardTitle className="text-base font-bold text-white flex items-center">
                  <Sparkles className="h-4 w-4 text-indigo-400 mr-2" />
                  Multimodal Evaluation Diagnostics
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  9-Phase breakdown: Speech, Visual Gestures, Slide OCR, and Ollama LLM Intelligence
                </CardDescription>
              </div>

              <div className="flex space-x-1 p-1 bg-slate-950/80 rounded-lg border border-slate-800 text-xs">
                <button
                  onClick={() => setActiveTab('metrics')}
                  className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'metrics' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'}`}
                >
                  Score Breakdown
                </button>
                <button
                  onClick={() => setActiveTab('report')}
                  className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'report' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'}`}
                >
                  Executive Report
                </button>
              </div>
            </CardHeader>

            <CardContent className="pt-6">
              {activeTab === 'metrics' ? (
                <div className="space-y-4">
                  {/* Category Scores */}
                  <div className="space-y-3">
                    <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-2">
                      <div className="flex justify-between text-xs font-semibold text-white">
                        <span>1. Speech Delivery & Vocal Clarity (Whisper + Signal Analysis)</span>
                        <span className="font-mono text-indigo-400">{report ? `${report.scores.clarity_and_delivery}%` : '--'}</span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${report ? report.scores.clarity_and_delivery : 0}%` }}></div>
                      </div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-2">
                      <div className="flex justify-between text-xs font-semibold text-white">
                        <span>2. Visual Engagement & Pose/Gesture (MediaPipe Mesh)</span>
                        <span className="font-mono text-sky-400">{report ? `${report.scores.visual_and_engagement}%` : '--'}</span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div className="bg-sky-500 h-full rounded-full" style={{ width: `${report ? report.scores.visual_and_engagement : 0}%` }}></div>
                      </div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 space-y-2">
                      <div className="flex justify-between text-xs font-semibold text-white">
                        <span>3. Slide Structure & Teaching Intelligence (OCR + Ollama Llama3.2 3B)</span>
                        <span className="font-mono text-emerald-400">{report ? `${report.scores.content_and_pedagogy}%` : '--'}</span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${report ? report.scores.content_and_pedagogy : 0}%` }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {report ? (
                    <div className="space-y-4">
                      <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20 space-y-2">
                        <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">Executive Recommendation Summary</h4>
                        <p className="text-xs text-slate-200">{report.recommendation.summary}</p>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                          <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center">
                            <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Key Strengths
                          </h4>
                          <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                            {report.strengths.map((str, i) => (
                              <li key={i}>{str}</li>
                            ))}
                          </ul>
                        </div>

                        <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-2">
                          <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center">
                            <AlertCircle className="h-3.5 w-3.5 mr-1" /> Growth Areas
                          </h4>
                          <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                            {report.weaknesses.map((weak, i) => (
                              <li key={i}>{weak}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="py-8 text-center text-slate-500 text-xs">
                      No report generated yet. Upload a video file to run the complete 9-phase evaluation.
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
