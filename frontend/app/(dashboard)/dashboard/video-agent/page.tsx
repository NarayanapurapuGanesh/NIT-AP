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
  Layers,
  FileText,
  ListOrdered,
  Image as ImageIcon
} from 'lucide-react';
import { TeachingVisualsGallery } from './TeachingVisualsGallery';

interface ProcessingStep {
  module_name: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'SKIPPED' | 'FAILED';
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  error?: string;
}

interface JobResponse {
  job_id: string;
  status: 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'PARTIAL';
  message: string;
  steps: ProcessingStep[];
}

interface FullReportDTO {
  jobId: string;
  video: {
    filename: string;
    durationSeconds: number;
    resolution: string;
  };
  summary: {
    shortSummary: string;
    topicsCovered: string[];
    concepts: string[];
    keywords: string[];
    technicalTerms: string[];
  };
  timeline: {
    totalEntries: number;
    durationSeconds: number;
    entries: any[];
  };
  ocr: any[];
}

export default function VideoAgentPage() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [videoPreviewUrl, setVideoPreviewUrl] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  
  const [jobStatus, setJobStatus] = useState<JobResponse | null>(null);
  const [report, setReport] = useState<FullReportDTO | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'status' | 'summary' | 'timeline' | 'visuals'>('status');

  const processVideoFile = async (uploadedFile: File) => {
    setAnalyzing(true);
    setFile(uploadedFile);
    setErrorMessage(null);
    setJobStatus(null);
    setReport(null);
    setActiveTab('status');

    // Create local object URL for instant video player preview
    const previewUrl = URL.createObjectURL(uploadedFile);
    setVideoPreviewUrl(previewUrl);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      // 1. Trigger the processing pipeline
      const res = await fetch('http://localhost:8005/video/process', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || errData.message || `Pipeline failed to start with status ${res.status}`);
      }

      const initialJob: JobResponse = await res.json();
      setJobStatus(initialJob);
      const jobId = initialJob.job_id;

      // 2. Poll for job status
      let currentJob = initialJob;
      while (currentJob.status !== 'COMPLETED' && currentJob.status !== 'FAILED') {
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const statusRes = await fetch(`http://localhost:8005/video/status/${jobId}`);
        if (!statusRes.ok) {
          throw new Error('Failed to fetch job status');
        }
        
        currentJob = await statusRes.json();
        setJobStatus(currentJob);
      }

      if (currentJob.status === 'FAILED') {
        const validationFailed = currentJob.steps.find((s: ProcessingStep) => s.module_name === 'validation' && s.status === 'FAILED');
        if (validationFailed) {
          throw new Error('This video does not meet the requirements for a teaching demonstration. Please re-upload a valid teaching video (ensure it has an active audio stream and meets the length requirements).');
        }
        throw new Error(currentJob.message || 'Pipeline processing failed.');
      }

      // 3. Fetch final report
      const reportRes = await fetch(`http://localhost:8005/video/report/${jobId}`);
      if (!reportRes.ok) {
        throw new Error('Failed to fetch evidence report');
      }
      
      const reportData: FullReportDTO = await reportRes.json();
      setReport(reportData);
      setActiveTab('summary');
      
    } catch (err: any) {
      console.error('Video processing failed:', err);
      setErrorMessage(err.message || 'Could not connect to Video Evidence Extraction Service (http://localhost:8005).');
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
            <span>Video Evidence Extraction Service</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Teaching Demonstration Extraction Engine</h1>
          <p className="text-xs text-slate-300">
            Offline-first AI Agent extracting transcripts, slide OCR, and teaching timelines.
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
            <span>{analyzing ? 'Processing Video...' : 'Upload Video File'}</span>
          </Button>
        </div>
      </div>

      {/* Video Upload Dropzone */}
      <div className="flex flex-col gap-6">
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current?.click()}
          className="w-full group relative cursor-pointer rounded-2xl border-2 border-dashed border-indigo-500/30 hover:border-indigo-500/60 bg-gradient-to-b from-indigo-950/20 via-slate-900/60 to-slate-950/80 p-8 text-center transition-all shadow-xl hover:shadow-indigo-500/10"
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
                Supported Formats: MP4, MOV, AVI, MKV, WEBM (Max 500MB)
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-red-950/60 border border-red-500/30 text-red-300 text-xs flex items-start space-x-3 shadow-lg">
          <AlertCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">Extraction Error</span>
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
                  <span className="flex items-center"><Clock className="h-3.5 w-3.5 text-sky-400 mr-1" /> Ready for AI Extraction</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Detailed Extraction Evidence */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-2xl">
            <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-slate-800/80">
              <div>
                <CardTitle className="text-base font-bold text-white flex items-center">
                  <Sparkles className="h-4 w-4 text-indigo-400 mr-2" />
                  Evidence Extraction Results
                </CardTitle>
                <CardDescription className="text-xs text-slate-400">
                  Transcripts, OCR, Timelines, and Summaries
                </CardDescription>
              </div>

              <div className="flex space-x-1 p-1 bg-slate-950/80 rounded-lg border border-slate-800 text-xs">
                <button
                  onClick={() => setActiveTab('status')}
                  className={`px-3 py-1 rounded-md transition-colors ${activeTab === 'status' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'}`}
                >
                  <Layers className="h-3.5 w-3.5 inline mr-1" /> Status
                </button>
                <button
                  onClick={() => setActiveTab('summary')}
                  disabled={!report}
                  className={`px-3 py-1 rounded-md transition-colors ${!report ? 'opacity-50 cursor-not-allowed' : ''} ${activeTab === 'summary' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'}`}
                >
                  <FileText className="h-3.5 w-3.5 inline mr-1" /> Summary
                </button>
                <button
                  onClick={() => setActiveTab('timeline')}
                  disabled={!report}
                  className={`px-3 py-1 rounded-md transition-colors ${!report ? 'opacity-50 cursor-not-allowed' : ''} ${activeTab === 'timeline' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'}`}
                >
                  <ListOrdered className="h-3.5 w-3.5 inline mr-1" /> Timeline
                </button>
                <button
                  onClick={() => setActiveTab('visuals')}
                  disabled={!report}
                  className={`px-3 py-1 rounded-md transition-colors ${!report ? 'opacity-50 cursor-not-allowed' : ''} ${activeTab === 'visuals' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-white'}`}
                >
                  <ImageIcon className="h-3.5 w-3.5 inline mr-1" /> Visuals
                </button>
              </div>
            </CardHeader>

            <CardContent className="pt-6">
              {activeTab === 'status' && (
                <div className="space-y-4">
                  {jobStatus ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                        <div className="text-sm font-bold text-white">Pipeline Diagnostics Dashboard</div>
                        <div className="text-xs font-semibold px-2 py-1 bg-slate-900 rounded-md border border-slate-700">
                          Status: <span className="text-indigo-400">{jobStatus.status}</span>
                        </div>
                      </div>
                      
                      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-950/50">
                        <table className="w-full text-left text-xs text-slate-300">
                          <thead className="bg-slate-900/80 text-slate-400 border-b border-slate-800">
                            <tr>
                              <th className="px-4 py-3 font-semibold">Stage</th>
                              <th className="px-4 py-3 font-semibold">Status</th>
                              <th className="px-4 py-3 font-semibold text-right">Duration</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800">
                            {jobStatus.steps.map((step) => {
                              const getStatusIcon = (status: string) => {
                                switch (status) {
                                  case 'COMPLETED': return '✅';
                                  case 'RUNNING': return '⏳';
                                  case 'FAILED': return '❌';
                                  case 'SKIPPED': return '⚠️';
                                  default: return '⚪';
                                }
                              };
                              
                              const getStatusClass = (status: string) => {
                                switch (status) {
                                  case 'COMPLETED': return 'text-emerald-400';
                                  case 'RUNNING': return 'text-amber-400 animate-pulse';
                                  case 'FAILED': return 'text-red-400';
                                  case 'SKIPPED': return 'text-orange-400';
                                  default: return 'text-slate-500';
                                }
                              };

                              return (
                                <tr key={step.module_name} className="hover:bg-slate-900/50 transition-colors">
                                  <td className="px-4 py-3 font-medium capitalize">{step.module_name.replace(/_/g, ' ')}</td>
                                  <td className="px-4 py-3">
                                    <span className={`inline-flex items-center space-x-1.5 ${getStatusClass(step.status)}`}>
                                      <span>{getStatusIcon(step.status)}</span>
                                      <span className="font-semibold">{step.status}</span>
                                    </span>
                                    {step.error && (
                                      <div className="mt-1 text-[10px] text-red-400/80 max-w-xs truncate" title={step.error}>
                                        {step.error}
                                      </div>
                                    )}
                                  </td>
                                  <td className="px-4 py-3 text-right font-mono text-slate-400">
                                    {step.duration_seconds !== undefined ? `${step.duration_seconds} s` : '-'}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ) : (
                    <div className="py-8 text-center text-slate-500 text-xs">
                      No job running. Upload a video file to extract evidence.
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'summary' && report && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20 space-y-2">
                    <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">Teaching Summary</h4>
                    <p className="text-xs text-slate-200">{report.summary.shortSummary}</p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                      <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center">
                        <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Topics Covered
                      </h4>
                      <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside">
                        {report.summary.topicsCovered.slice(0, 5).map((topic, i) => (
                          <li key={i}>{topic}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="p-4 rounded-xl bg-sky-950/20 border border-sky-500/20 space-y-2">
                      <h4 className="text-xs font-bold text-sky-400 uppercase tracking-wider flex items-center">
                        <Sparkles className="h-3.5 w-3.5 mr-1" /> Keywords
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {report.summary.keywords.slice(0, 8).map((kw, i) => (
                          <span key={i} className="px-2 py-1 bg-sky-500/10 text-sky-300 rounded text-[10px]">{kw}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {activeTab === 'timeline' && report && (
                <div className="space-y-4 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                  {report.timeline.entries.map((entry: any, idx: number) => (
                    <div key={idx} className="flex gap-4 p-3 rounded-lg bg-slate-900/50 border border-slate-800">
                      <div className="text-xs font-mono text-indigo-400 shrink-0">
                        {entry.timestampFormatted || `${Math.floor(entry.timestamp)}s`}
                      </div>
                      <div className="space-y-1 text-xs">
                        {entry.transcriptText && (
                          <p className="text-slate-300">
                            <span className="text-sky-500 mr-2">🗣️</span>
                            {entry.transcriptText}
                          </p>
                        )}
                        {entry.ocrText && (
                          <p className="text-slate-400 italic">
                            <span className="text-emerald-500 mr-2">📄 OCR:</span>
                            {entry.ocrText}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'visuals' && report && (
                <TeachingVisualsGallery jobId={jobStatus?.job_id || ""} />
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
