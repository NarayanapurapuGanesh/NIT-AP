'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  checkInteractionHealth,
  startInteractionSession,
  sendFacultyMessage,
  pauseSession as apiPauseSession,
  resumeSession as apiResumeSession,
  endInteractionSession,
  HealthCheckResponse,
  InteractionAnalyticsSnapshot,
  InteractionSessionReport,
} from '@/lib/api/interaction';

// ═══════════════════════════════════════════════════════════════════
//  Constants & Color Tokens
// ═══════════════════════════════════════════════════════════════════

const BLOOM_LEVELS = [
  { name: 'Remember', color: '#6366f1', desc: 'Recalling definitions & terms' },
  { name: 'Understand', color: '#8b5cf6', desc: 'Explaining underlying concepts' },
  { name: 'Apply', color: '#06b6d4', desc: 'Working through practical scenarios' },
  { name: 'Analyze', color: '#10b981', desc: 'Comparing trade-offs & edge cases' },
  { name: 'Evaluate', color: '#f59e0b', desc: 'Critiquing & justifying methods' },
  { name: 'Create', color: '#ec4899', desc: 'Architecting novel solutions' },
];

const BLOOM_COLOR_MAP: Record<string, string> = {
  Remember: '#6366f1',
  Understand: '#8b5cf6',
  Apply: '#06b6d4',
  Analyze: '#10b981',
  Evaluate: '#f59e0b',
  Create: '#ec4899',
};

const STUDENT_LEVELS = [
  {
    id: 'Beginner',
    label: 'Foundational / 1st Year Student',
    desc: 'Lacks technical jargon; tests if you can explain from scratch with simple real-world analogies.',
    icon: '🌱',
    color: '#10b981',
  },
  {
    id: 'Average',
    label: 'Undergraduate (2nd / 3rd Year B.Tech)',
    desc: 'Standard engineering student; understands basics but asks conceptual questions and code examples.',
    icon: '🎓',
    color: '#6366f1',
  },
  {
    id: 'Curious',
    label: 'Advanced / Inquisitive Learner',
    desc: 'Asks deep "why" questions, edge cases, performance trade-offs, and real-world system behavior.',
    icon: '⚡',
    color: '#8b5cf6',
  },
];

const PRESET_DOMAINS = [
  {
    subject: 'Object-Oriented Programming',
    dept: 'Computer Science',
    suggestedTopic: 'Inheritance vs Composition and Polymorphism',
  },
  {
    subject: 'Data Structures & Algorithms',
    dept: 'Computer Science',
    suggestedTopic: 'Binary Search Trees vs Hash Tables and Collision Handling',
  },
  {
    subject: 'Operating Systems',
    dept: 'Computer Science',
    suggestedTopic: 'Deadlocks, Mutex Locks, and Process Synchronization',
  },
  {
    subject: 'Database Management Systems',
    dept: 'Information Technology',
    suggestedTopic: 'Database Normalization (1NF to BCNF) and Indexing',
  },
  {
    subject: 'Computer Networks',
    dept: 'Computer Science',
    suggestedTopic: 'TCP 3-Way Handshake vs UDP and Flow Control',
  },
  {
    subject: 'Machine Learning',
    dept: 'Artificial Intelligence',
    suggestedTopic: 'Overfitting, Regularization, and Gradient Descent',
  },
];

interface ChatMessage {
  id: string;
  speaker: 'Student' | 'Faculty' | 'System';
  message: string;
  bloomLevel: string;
  turnNumber: number;
  timestamp: string;
}

// ═══════════════════════════════════════════════════════════════════
//  Main Interaction Page
// ═══════════════════════════════════════════════════════════════════

export default function InteractionPage() {
  // Session State
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<
    'IDLE' | 'INITIALIZING' | 'ACTIVE' | 'PAUSED' | 'COMPLETING' | 'COMPLETED' | 'ERROR'
  >('IDLE');
  const [initStage, setInitStage] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Configuration State
  const [subject, setSubject] = useState('Object-Oriented Programming');
  const [topic, setTopic] = useState('Inheritance, Polymorphism & Encapsulation');
  const [department, setDepartment] = useState('Computer Science');
  const [studentLevel, setStudentLevel] = useState('Average');
  const [maxTurns, setMaxTurns] = useState(12);

  // Health state
  const [health, setHealth] = useState<HealthCheckResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Conversation & Analytics
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [analytics, setAnalytics] = useState<InteractionAnalyticsSnapshot | null>(null);
  const [report, setReport] = useState<InteractionSessionReport | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Check health on mount
  const runHealthCheck = useCallback(async () => {
    setHealthLoading(true);
    try {
      const res = await checkInteractionHealth();
      setHealth(res);
    } catch {
      setHealth(null);
    } finally {
      setHealthLoading(false);
    }
  }, []);

  useEffect(() => {
    runHealthCheck();
  }, [runHealthCheck]);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  // Session duration timer
  useEffect(() => {
    if (sessionStatus === 'ACTIVE') {
      timerRef.current = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [sessionStatus]);

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // ─── Lifecycle Actions ──────────────────────────────────────────

  const handleStartSession = async () => {
    setErrorMessage(null);
    setSessionStatus('INITIALIZING');
    setInitStage('Connecting to local AI evaluation engine...');

    const combinedSubject = topic.trim()
      ? `${subject} — ${topic.trim()}`
      : subject;

    try {
      await new Promise((r) => setTimeout(r, 400));
      setInitStage(`Preparing student inquiries for ${subject}...`);

      const response = await startInteractionSession({
        subject: combinedSubject,
        department,
        persona_type: studentLevel,
        max_turns: maxTurns,
      });

      setSessionId(response.session_id);
      setSessionStatus('ACTIVE');
      setElapsedSeconds(0);

      // Add opening student question
      setMessages([
        {
          id: 'turn-1',
          speaker: 'Student',
          message: response.opening_message,
          bloomLevel: response.current_bloom_level || 'Remember',
          turnNumber: 1,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);

      setAnalytics({
        teaching_score: 0,
        communication_score: 0,
        engagement_score: 0,
        student_satisfaction: 0,
        learning_gain: 0.1,
        current_bloom_level: response.current_bloom_level || 'Remember',
        turn_number: 1,
        max_turns: response.max_turns,
        current_topic: combinedSubject,
        bloom_distribution: { [response.current_bloom_level || 'Remember']: 1 },
        total_misconceptions: 0,
        corrected_misconceptions: 0,
        missed_misconceptions: 0,
        total_evidence_packets: 0,
        understanding_estimate: 0.15,
        concepts_explored: 1,
      });
    } catch (err: any) {
      setSessionStatus('ERROR');
      setErrorMessage(err.message || 'Failed to initialize teaching interaction');
    }
  };

  const handleSendMessage = async () => {
    if (!sessionId || !inputText.trim() || isProcessing || sessionStatus !== 'ACTIVE') return;

    const facultyContent = inputText.trim();
    setInputText('');
    setIsProcessing(true);

    const currentTurn = (analytics?.turn_number || 1) + 1;

    // Append faculty message immediately
    const facultyMsg: ChatMessage = {
      id: `faculty-${Date.now()}`,
      speaker: 'Faculty',
      message: facultyContent,
      bloomLevel: analytics?.current_bloom_level || 'Remember',
      turnNumber: currentTurn,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, facultyMsg]);

    try {
      const response = await sendFacultyMessage(sessionId, {
        message: facultyContent,
      });

      // Append student reply
      const studentMsg: ChatMessage = {
        id: `student-${Date.now()}`,
        speaker: 'Student',
        message: response.student_message,
        bloomLevel: response.current_bloom_level || 'Remember',
        turnNumber: response.turn_number,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, studentMsg]);
      setAnalytics(response.analytics);

      if (response.session_complete) {
        handleEndSession();
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit response');
    } finally {
      setIsProcessing(false);
      setTimeout(() => textareaRef.current?.focus(), 100);
    }
  };

  const handlePauseResume = async () => {
    if (!sessionId) return;
    try {
      if (sessionStatus === 'ACTIVE') {
        await apiPauseSession(sessionId);
        setSessionStatus('PAUSED');
      } else if (sessionStatus === 'PAUSED') {
        await apiResumeSession(sessionId);
        setSessionStatus('ACTIVE');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to toggle pause');
    }
  };

  const handleEndSession = async () => {
    if (!sessionId) return;
    setIsProcessing(true);
    setSessionStatus('COMPLETING');

    try {
      const finalReport = await endInteractionSession(sessionId);
      setReport(finalReport);
      setSessionStatus('COMPLETED');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to finalize session report');
      setSessionStatus('ACTIVE');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setSessionId(null);
    setSessionStatus('IDLE');
    setMessages([]);
    setInputText('');
    setAnalytics(null);
    setReport(null);
    setErrorMessage(null);
    setElapsedSeconds(0);
    runHealthCheck();
  };

  // ═══════════════════════════════════════════════════════════════════
  //  View 1: Configuration & Pre-Flight Setup
  // ═══════════════════════════════════════════════════════════════════

  if (sessionStatus === 'IDLE' || sessionStatus === 'INITIALIZING' || sessionStatus === 'ERROR') {
    return (
      <div className="min-h-screen bg-[#07080b] text-[#e2e8f0] p-6 lg:p-10 flex flex-col justify-center items-center font-sans relative overflow-hidden">
        {/* Ambient glows */}
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-4xl bg-[#0f111a]/80 backdrop-blur-2xl border border-white/10 rounded-2xl p-6 lg:p-10 shadow-2xl relative z-10"
        >
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-8 border-b border-white/10">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-3">
                <span>👨‍🏫 Faculty Evaluation</span>
              </div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white tracking-tight">
                Live Teaching Interaction Evaluation
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                The AI Student will ask conceptual questions, doubts, and edge cases on your chosen topic to evaluate your pedagogical clarity, technical accuracy, and adaptability.
              </p>
            </div>

            {/* Health Badge */}
            <div className="flex items-center gap-3 bg-white/[0.03] border border-white/10 px-4 py-2.5 rounded-xl shrink-0">
              <div
                className={`w-2.5 h-2.5 rounded-full ${
                  health?.status === 'healthy'
                    ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]'
                    : health?.status === 'degraded'
                    ? 'bg-amber-400 shadow-[0_0_8px_#fbbf24]'
                    : 'bg-rose-500 shadow-[0_0_8px_#f43f5e]'
                }`}
              />
              <div className="text-xs">
                <div className="font-semibold text-slate-200">
                  {healthLoading
                    ? 'Checking Engine...'
                    : health?.status === 'healthy'
                    ? 'Evaluator Engine Active'
                    : 'Engine Offline'}
                </div>
                <div className="text-slate-500 text-[11px]">
                  {health?.student_model || 'llama3.2:3b'} (Local Inference)
                </div>
              </div>
              <button
                onClick={runHealthCheck}
                className="ml-2 text-slate-400 hover:text-white transition-colors"
                title="Refresh Status"
              >
                🔄
              </button>
            </div>
          </div>

          {/* Error Alert */}
          {errorMessage && (
            <div className="mt-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-start gap-3">
              <span className="text-lg">⚠️</span>
              <div className="flex-1">
                <div className="font-semibold">Notice</div>
                <div className="text-xs text-rose-300/80 mt-0.5">{errorMessage}</div>
              </div>
              <button
                onClick={() => setErrorMessage(null)}
                className="text-xs text-rose-400 hover:text-white"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Subject & Topic Details */}
          <div className="space-y-6 mt-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Subject */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Course / Subject Domain
                </label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g. Data Structures & Algorithms"
                  className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>

              {/* Department */}
              <div>
                <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Department
                </label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  placeholder="e.g. Computer Science & Engineering"
                  className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>
            </div>

            {/* Specific Topic to Teach */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                Specific Topic to Teach in this Session
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Binary Search Trees & AVL Balancing, Polymorphism & Virtual Functions"
                className="w-full bg-white/[0.04] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />
              <p className="text-[11px] text-slate-400 mt-1.5">
                The AI student will ask specific, curriculum-aligned doubts directly relating to this topic.
              </p>

              {/* Quick Presets */}
              <div className="flex flex-wrap gap-2 mt-3">
                <span className="text-xs text-slate-500 self-center mr-1">Quick Select:</span>
                {PRESET_DOMAINS.map((item) => (
                  <button
                    key={item.subject}
                    type="button"
                    onClick={() => {
                      setSubject(item.subject);
                      setDepartment(item.dept);
                      setTopic(item.suggestedTopic);
                    }}
                    className={`text-[11px] px-3 py-1.5 rounded-lg border transition-all ${
                      subject === item.subject
                        ? 'bg-indigo-600/30 border-indigo-500/50 text-indigo-300 font-medium'
                        : 'bg-white/[0.02] border-white/10 text-slate-400 hover:border-white/20'
                    }`}
                  >
                    {item.subject}
                  </button>
                ))}
              </div>
            </div>

            {/* Target Student Academic Level */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
                Target Student Academic Level
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {STUDENT_LEVELS.map((lvl) => {
                  const isSelected = studentLevel === lvl.id;
                  return (
                    <button
                      key={lvl.id}
                      type="button"
                      onClick={() => setStudentLevel(lvl.id)}
                      className={`p-4 rounded-xl border text-left transition-all relative overflow-hidden group ${
                        isSelected
                          ? 'bg-indigo-600/10 border-indigo-500/80 shadow-md shadow-indigo-600/10 ring-1 ring-indigo-500/50'
                          : 'bg-white/[0.02] border-white/10 hover:border-white/20 hover:bg-white/[0.04]'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className="text-xl">{lvl.icon}</span>
                        <span className="font-semibold text-sm text-slate-100">{lvl.label}</span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">{lvl.desc}</p>
                      {isSelected && (
                        <div className="absolute top-2 right-2 w-2 h-2 rounded-full bg-indigo-400 shadow-[0_0_6px_#818cf8]" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Evaluation Turns */}
            <div>
              <label className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
                Session Length
              </label>
              <div className="grid grid-cols-3 gap-3 max-w-sm">
                {[8, 12, 16].map((num) => (
                  <button
                    key={num}
                    type="button"
                    onClick={() => setMaxTurns(num)}
                    className={`py-2.5 rounded-xl text-xs font-semibold border transition-all ${
                      maxTurns === num
                        ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-600/30'
                        : 'bg-white/[0.02] border-white/10 text-slate-400 hover:text-white hover:bg-white/[0.05]'
                    }`}
                  >
                    {num} Turns {num === 12 ? '(Standard)' : ''}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Start Action Bar */}
          <div className="mt-10 pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-slate-500">
              ⚡ Local AI student will ask questions and evaluate your teaching live
            </div>
            <button
              onClick={handleStartSession}
              disabled={sessionStatus === 'INITIALIZING' || !subject.trim()}
              className="w-full sm:w-auto px-8 py-3.5 rounded-xl font-semibold text-sm text-white bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 hover:opacity-90 shadow-lg shadow-indigo-600/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {sessionStatus === 'INITIALIZING' ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>{initStage || 'Initializing Student...'}</span>
                </>
              ) : (
                <>
                  <span>🚀 Start Teaching Session</span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════
  //  View 2: Completed Session Report
  // ═══════════════════════════════════════════════════════════════════

  if (sessionStatus === 'COMPLETED' && report) {
    const pct = (v: number) => `${Math.round((v || 0) * 100)}%`;

    return (
      <div className="min-h-screen bg-[#07080b] text-[#e2e8f0] p-6 lg:p-12 font-sans">
        <div className="max-w-5xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
                <span>✓ Evaluation Report</span>
              </div>
              <h1 className="text-3xl font-extrabold text-white tracking-tight">
                Teaching Intelligence Assessment
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                {report.subject} • {report.department} • {report.total_turns} Turns • {report.duration}
              </p>
            </div>
            <button
              onClick={handleReset}
              className="px-5 py-2.5 bg-white/[0.04] hover:bg-white/[0.08] border border-white/10 rounded-xl text-sm font-medium text-slate-200 transition-all flex items-center gap-2 self-start sm:self-auto"
            >
              <span>← Start New Session</span>
            </button>
          </div>

          {/* Hero Score Banner */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-8 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-[#0e111a] to-purple-950/30 border border-indigo-500/20 relative overflow-hidden shadow-2xl">
            <div className="md:col-span-2 flex flex-col justify-center space-y-3">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                Overall Teaching Performance Score
              </span>
              <div className="flex items-baseline gap-4">
                <span className="text-6xl font-black bg-gradient-to-r from-white via-indigo-200 to-indigo-400 bg-clip-text text-transparent">
                  {pct(report.overall_score)}
                </span>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                    report.recommendation === 'STRONG'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : report.recommendation === 'GOOD'
                      ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                      : report.recommendation === 'AVERAGE'
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                  }`}
                >
                  {report.recommendation}
                </span>
              </div>
              <p className="text-slate-400 text-sm leading-relaxed max-w-xl">
                Evaluated against core pedagogical criteria: concept accuracy, explanation clarity, responsiveness to student questions, and use of concrete examples.
              </p>
            </div>

            <div className="flex flex-col justify-center space-y-2.5 p-5 rounded-xl bg-white/[0.02] border border-white/5">
              <div className="text-xs text-slate-400">Evaluation Confidence</div>
              <div className="text-2xl font-bold text-white">{pct(report.confidence)}</div>
              <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-indigo-500 h-full rounded-full"
                  style={{ width: `${report.confidence * 100}%` }}
                />
              </div>
              <span className="text-[11px] text-slate-500">Based on {report.total_turns} multi-turn conversational exchanges</span>
            </div>
          </div>

          {/* Dimension Scores Grid */}
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">
              Teaching Dimensions Evaluation
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label: 'Technical Accuracy', val: report.scores.technical_accuracy, icon: '🎯' },
                { label: 'Concept Clarity', val: report.scores.concept_clarity, icon: '💡' },
                { label: 'Doubt Resolution', val: report.scores.doubt_resolution, icon: '🤝' },
                { label: 'Adaptability', val: report.scores.pedagogical_adaptability, icon: '🔄' },
                { label: 'Explanation Structure', val: report.scores.explanation_structure, icon: '📐' },
                { label: 'Example Quality', val: report.scores.example_quality, icon: '🧪' },
                { label: 'Bloom Depth', val: report.scores.bloom_depth, icon: '📈' },
                { label: 'Misconception Handling', val: report.scores.misconception_handling, icon: '🛡️' },
              ].map((dim) => (
                <div
                  key={dim.label}
                  className="p-4 rounded-xl bg-white/[0.02] border border-white/10 flex flex-col justify-between space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-lg">{dim.icon}</span>
                    <span className="text-xs font-bold text-indigo-400">{pct(dim.val)}</span>
                  </div>
                  <div>
                    <div className="text-xs text-slate-300 font-medium">{dim.label}</div>
                    <div className="w-full bg-white/5 h-1.5 rounded-full mt-2 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full"
                        style={{ width: `${dim.val * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bloom Profile Distribution */}
          <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4">
              Cognitive Level Progression (Bloom's Taxonomy)
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
              {BLOOM_LEVELS.map((level) => {
                const ratio = report.bloom_profile[level.name] || 0;
                return (
                  <div
                    key={level.name}
                    className="p-3 rounded-xl bg-white/[0.01] border border-white/5 text-center flex flex-col items-center"
                  >
                    <span className="text-xs font-semibold text-slate-300 mb-1">{level.name}</span>
                    <div className="h-20 w-full flex items-end justify-center py-1">
                      <div
                        className="w-8 rounded-t-lg transition-all duration-500"
                        style={{
                          height: `${Math.max(8, ratio * 70)}px`,
                          backgroundColor: level.color,
                          boxShadow: `0 0 12px ${level.color}40`,
                        }}
                      />
                    </div>
                    <span className="text-xs font-bold text-slate-400 mt-2">{pct(ratio)}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-emerald-950/20 border border-emerald-500/20 space-y-4">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm uppercase tracking-wider">
                <span>✓ Observed Teaching Strengths</span>
              </div>
              <ul className="space-y-2.5">
                {report.strengths.length > 0 ? (
                  report.strengths.map((str, i) => (
                    <li key={i} className="text-xs text-slate-300 flex items-start gap-2.5 leading-relaxed">
                      <span className="text-emerald-400 mt-0.5">•</span>
                      <span>{str}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-xs text-slate-500 italic">No specific strengths documented.</li>
                )}
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-500/20 space-y-4">
              <div className="flex items-center gap-2 text-rose-400 font-bold text-sm uppercase tracking-wider">
                <span>⚠ Recommendations for Improvement</span>
              </div>
              <ul className="space-y-2.5">
                {report.weaknesses.length > 0 ? (
                  report.weaknesses.map((wk, i) => (
                    <li key={i} className="text-xs text-slate-300 flex items-start gap-2.5 leading-relaxed">
                      <span className="text-rose-400 mt-0.5">•</span>
                      <span>{wk}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-xs text-slate-500 italic">No major pedagogical weaknesses observed.</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ═══════════════════════════════════════════════════════════════════
  //  View 3: Active Interactive Teaching Workspace
  // ═══════════════════════════════════════════════════════════════════

  return (
    <div className="h-screen bg-[#07080b] text-[#e2e8f0] flex flex-col font-sans overflow-hidden">
      {/* Top Session Status Bar */}
      <header className="h-16 px-6 bg-[#0c0e15] border-b border-white/10 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <div className="w-9 h-9 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-lg">
            🎓
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-bold text-sm text-white">{subject}</h2>
              {topic && (
                <span className="text-xs px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-300">
                  {topic}
                </span>
              )}
            </div>
            <div className="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5">
              <span>Class Level: <strong className="text-indigo-300">{studentLevel}</strong></span>
              <span>•</span>
              <span className="font-mono text-indigo-400">{formatTimer(elapsedSeconds)}</span>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={handlePauseResume}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
              sessionStatus === 'PAUSED'
                ? 'bg-emerald-500/20 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/30'
                : 'bg-amber-500/20 border-amber-500/30 text-amber-300 hover:bg-amber-500/30'
            }`}
          >
            {sessionStatus === 'PAUSED' ? '▶ Resume' : '⏸ Pause'}
          </button>
          <button
            onClick={handleEndSession}
            disabled={isProcessing}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/30 text-rose-300 transition-all disabled:opacity-50"
          >
            ⏹ Finish & Evaluate
          </button>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_360px] overflow-hidden">
        {/* Left Column: Chat Dialogue Area */}
        <main className="flex flex-col h-full bg-[#08090e] overflow-hidden">
          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            <AnimatePresence initial={false}>
              {messages.map((msg) => {
                const isStudent = msg.speaker === 'Student';
                const bloomColor = BLOOM_COLOR_MAP[msg.bloomLevel] || '#6366f1';

                return (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex flex-col ${isStudent ? 'items-start' : 'items-end'}`}
                  >
                    {/* Speaker Header */}
                    <div className="flex items-center gap-2 mb-1.5 px-1">
                      <span className="text-[11px] font-bold text-slate-400">
                        {isStudent ? '🎓 Student Question / Doubt' : '👨‍🏫 Your Explanation'}
                      </span>
                      {isStudent && (
                        <span
                          className="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase"
                          style={{
                            backgroundColor: `${bloomColor}18`,
                            color: bloomColor,
                            border: `1px solid ${bloomColor}40`,
                          }}
                        >
                          {msg.bloomLevel}
                        </span>
                      )}
                      <span className="text-[10px] text-slate-600">{msg.timestamp}</span>
                    </div>

                    {/* Bubble Content */}
                    <div
                      className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed ${
                        isStudent
                          ? 'bg-[#121524] border border-indigo-500/20 text-slate-100 rounded-tl-sm shadow-lg shadow-indigo-950/10'
                          : 'bg-gradient-to-r from-emerald-950/40 to-teal-950/40 border border-emerald-500/30 text-emerald-50 rounded-tr-sm shadow-lg'
                      }`}
                    >
                      {msg.message}
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>

            {/* AI Student Thinking Indicator */}
            {isProcessing && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-3 p-4 bg-[#121524]/60 border border-indigo-500/20 rounded-2xl max-w-xs"
              >
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" />
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.2s]" />
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.4s]" />
                </div>
                <span className="text-xs text-indigo-300 font-medium">Student reflecting & synthesizing...</span>
              </motion.div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Faculty Response Input Box */}
          <div className="p-4 bg-[#0c0e15] border-t border-white/10 relative">
            {sessionStatus === 'PAUSED' && (
              <div className="absolute inset-0 bg-[#07080b]/80 backdrop-blur-sm z-20 flex items-center justify-center gap-3">
                <span className="text-xs text-amber-300 font-semibold">Session is Paused</span>
                <button
                  onClick={handlePauseResume}
                  className="px-3 py-1 bg-indigo-600 text-white text-xs font-semibold rounded-lg"
                >
                  Resume Session
                </button>
              </div>
            )}

            <div className="flex flex-col gap-2">
              <textarea
                ref={textareaRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={isProcessing || sessionStatus !== 'ACTIVE'}
                placeholder="Explain the concept clearly to the student... (Press Enter to send, Shift+Enter for new line)"
                rows={3}
                className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-3.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none transition-colors disabled:opacity-40"
              />

              <div className="flex items-center justify-between pt-1">
                <span className="text-[11px] text-slate-500">
                  Tip: Explain clearly, give examples/analogies, and verify the student's doubt is resolved.
                </span>
                <button
                  onClick={handleSendMessage}
                  disabled={!inputText.trim() || isProcessing || sessionStatus !== 'ACTIVE'}
                  className="px-6 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all disabled:opacity-40 shadow-lg shadow-indigo-600/20"
                >
                  {isProcessing ? 'Evaluating...' : 'Send Explanation ↵'}
                </button>
              </div>
            </div>
          </div>
        </main>

        {/* Right Column: Live Progress & Cognitive Mapping */}
        <aside className="h-full bg-[#0a0c12] border-l border-white/10 p-6 flex flex-col justify-between overflow-y-auto space-y-6">
          <div className="space-y-6">
            {/* Turn Progress Card */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-400 uppercase tracking-wider">Turn Progress</span>
                <span className="font-mono text-indigo-400 font-semibold">
                  {analytics?.turn_number || 1} / {maxTurns}
                </span>
              </div>
              <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-indigo-500 h-full rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(100, ((analytics?.turn_number || 1) / maxTurns) * 100)}%` }}
                />
              </div>
            </div>

            {/* Bloom's Cognitive Progression */}
            <div className="space-y-3">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Cognitive Level (Bloom's Taxonomy)
              </span>
              <div className="space-y-2">
                {BLOOM_LEVELS.map((b) => {
                  const isCurrent = analytics?.current_bloom_level === b.name;
                  return (
                    <div
                      key={b.name}
                      className={`p-2.5 rounded-lg border text-xs transition-all flex items-center justify-between ${
                        isCurrent
                          ? 'bg-white/[0.06] shadow-md'
                          : 'bg-white/[0.01] border-white/5 text-slate-500 opacity-60'
                      }`}
                      style={{ borderColor: isCurrent ? b.color : 'transparent' }}
                    >
                      <div className="flex items-center gap-2">
                        <div
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: b.color }}
                        />
                        <span className={`font-semibold ${isCurrent ? 'text-white' : 'text-slate-400'}`}>
                          {b.name}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400">{b.desc}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Student Understanding Metric */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-400 uppercase tracking-wider">
                  Student Comprehension Meter
                </span>
                <span className="font-bold text-indigo-300">
                  {Math.round((analytics?.understanding_estimate || 0.1) * 100)}%
                </span>
              </div>
              <div className="w-full bg-white/5 h-2 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500 bg-gradient-to-r from-amber-500 via-indigo-500 to-emerald-400"
                  style={{ width: `${(analytics?.understanding_estimate || 0.1) * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Bottom Guidelines Note */}
          <div className="p-3 rounded-lg bg-indigo-950/20 border border-indigo-500/20 text-[11px] text-slate-400 leading-relaxed">
            💡 <strong>Evaluation Notice:</strong> Numerical score metrics are strictly computed offline to eliminate observer bias during active teaching.
          </div>
        </aside>
      </div>
    </div>
  );
}
