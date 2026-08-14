'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ═══════════════════════════════════════════════════════════════════
//  Types
// ═══════════════════════════════════════════════════════════════════

interface Message {
  id: string;
  role: 'student' | 'faculty' | 'system';
  content: string;
  turnNumber: number;
  bloomLevel: string;
  timestamp: Date;
}

interface AnalyticsSnapshot {
  teachingScore: number;
  communicationScore: number;
  engagementScore: number;
  studentSatisfaction: number;
  learningGain: number;
  currentBloomLevel: string;
  turnNumber: number;
  maxTurns: number;
  currentTopic: string;
  bloomDistribution: Record<string, number>;
  totalMisconceptions: number;
  correctedMisconceptions: number;
  missedMisconceptions: number;
  totalEvidencePackets: number;
  understandingEstimate: number;
}

interface SessionReport {
  sessionId: string;
  overallTeachingEffectiveness: number;
  scores: {
    teaching: number;
    communication: number;
    engagement: number;
    studentSatisfaction: number;
    learningGain: number;
    bloomCoverage: number;
  };
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  evidence: Array<{
    turnNumber: number;
    type: string;
    score: number;
    justification: string;
  }>;
  totalTurns: number;
  duration: string;
  personaUsed: string;
  subject: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://localhost:7150/api/v1';

const BLOOM_COLORS: Record<string, string> = {
  Remember: '#6366f1',
  Understand: '#8b5cf6',
  Apply: '#a855f7',
  Analyze: '#d946ef',
  Evaluate: '#ec4899',
  Create: '#f43f5e',
};

const BLOOM_ORDER = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'];

// ═══════════════════════════════════════════════════════════════════
//  Main Page Component
// ═══════════════════════════════════════════════════════════════════

export default function InteractionPage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionActive, setSessionActive] = useState(false);
  const [sessionPaused, setSessionPaused] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [analytics, setAnalytics] = useState<AnalyticsSnapshot | null>(null);
  const [report, setReport] = useState<SessionReport | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [showSetup, setShowSetup] = useState(true);

  // Setup form
  const [subject, setSubject] = useState('Object-Oriented Programming');
  const [department, setDepartment] = useState('Computer Science');
  const [persona, setPersona] = useState('Curious');
  const [candidateId] = useState('00000000-0000-0000-0000-000000000001');

  const chatEndRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Timer
  useEffect(() => {
    if (sessionActive && !sessionPaused) {
      timerRef.current = setInterval(() => setElapsedTime(t => t + 1), 1000);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [sessionActive, sessionPaused]);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  };

  // ─── API Calls ──────────────────────────────────────────────────

  const startSession = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/interaction/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidateApplicationId: candidateId,
          subject, department,
          personaOverride: persona,
          maxTurns: 20,
        }),
      });
      const data = await res.json();
      setSessionId(data.sessionId);
      setSessionActive(true);
      setShowSetup(false);
      setMessages([{
        id: crypto.randomUUID(),
        role: 'student',
        content: data.openingStudentMessage,
        turnNumber: 1,
        bloomLevel: data.initialBloomLevel || 'Remember',
        timestamp: new Date(),
      }]);
      setAnalytics({
        teachingScore: 0, communicationScore: 0, engagementScore: 0,
        studentSatisfaction: 0, learningGain: 0,
        currentBloomLevel: data.initialBloomLevel || 'Remember',
        turnNumber: 1, maxTurns: 20, currentTopic: subject,
        bloomDistribution: { Remember: 1 },
        totalMisconceptions: 0, correctedMisconceptions: 0, missedMisconceptions: 0,
        totalEvidencePackets: 0, understandingEstimate: 0.1,
      });
    } catch (e) { console.error('Failed to start session:', e); }
    setIsLoading(false);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || isLoading) return;
    const msg = inputMessage.trim();
    setInputMessage('');

    // Add faculty message immediately
    const facultyMsg: Message = {
      id: crypto.randomUUID(), role: 'faculty', content: msg,
      turnNumber: (analytics?.turnNumber || 0) + 1,
      bloomLevel: analytics?.currentBloomLevel || 'Remember',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, facultyMsg]);
    setIsTyping(true);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/interaction/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, message: msg }),
      });
      const data = await res.json();

      // Add student response
      const studentMsg: Message = {
        id: crypto.randomUUID(), role: 'student', content: data.studentMessage,
        turnNumber: data.turnNumber,
        bloomLevel: data.currentBloomLevel || 'Remember',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, studentMsg]);

      if (data.analytics) setAnalytics(data.analytics);
      if (data.sessionComplete) {
        setSessionComplete(true);
        setSessionActive(false);
      }
    } catch (e) { console.error('Failed to send message:', e); }
    setIsTyping(false);
    setIsLoading(false);
  };

  const endSession = async () => {
    if (!sessionId) return;
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/interaction/end?sessionId=${sessionId}`, { method: 'POST' });
      const data = await res.json();
      setReport(data);
      setSessionComplete(true);
      setSessionActive(false);
    } catch (e) { console.error('Failed to end session:', e); }
    setIsLoading(false);
  };

  const pauseSession = async () => {
    if (!sessionId) return;
    await fetch(`${API_BASE}/interaction/${sessionId}/pause`, { method: 'POST' });
    setSessionPaused(true);
  };

  const resumeSession = async () => {
    if (!sessionId) return;
    await fetch(`${API_BASE}/interaction/${sessionId}/resume`, { method: 'POST' });
    setSessionPaused(false);
  };

  // ─── Render ──────────────────────────────────────────────────────

  if (showSetup) {
    return <SetupScreen
      subject={subject} setSubject={setSubject}
      department={department} setDepartment={setDepartment}
      persona={persona} setPersona={setPersona}
      onStart={startSession} isLoading={isLoading}
    />;
  }

  if (report) {
    return <ReportView report={report} onClose={() => setShowSetup(true)} />;
  }

  return (
    <div className="interaction-layout">
      {/* Left Panel — Conversation History */}
      <aside className="panel panel-left">
        <div className="panel-header">
          <h3>💬 Conversation</h3>
          <span className="turn-badge">{analytics?.turnNumber || 0}/{analytics?.maxTurns || 20}</span>
        </div>
        <div className="chat-container">
          <AnimatePresence>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
          </AnimatePresence>
          {isTyping && <TypingIndicator />}
          <div ref={chatEndRef} />
        </div>
        <div className="chat-input-area">
          <textarea
            value={inputMessage}
            onChange={e => setInputMessage(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
            placeholder={sessionPaused ? 'Session paused...' : 'Type your explanation...'}
            disabled={isLoading || sessionPaused || sessionComplete}
            rows={3}
          />
          <button onClick={sendMessage} disabled={isLoading || !inputMessage.trim() || sessionPaused}
                  className="btn-send">
            {isLoading ? '⏳' : '📤'} Send
          </button>
        </div>
      </aside>

      {/* Right Panel — Analytics Dashboard */}
      <main className="panel panel-right">
        <div className="panel-header">
          <h3>📊 Teaching Analytics</h3>
          <span className="timer">{formatTime(elapsedTime)}</span>
        </div>
        {analytics && <AnalyticsDashboard analytics={analytics} />}

        {/* Session Controls */}
        <div className="session-controls">
          {sessionPaused ? (
            <button onClick={resumeSession} className="btn-control btn-resume">▶️ Resume</button>
          ) : (
            <button onClick={pauseSession} className="btn-control btn-pause">⏸️ Pause</button>
          )}
          <button onClick={endSession} className="btn-control btn-end" disabled={isLoading}>
            ⏹️ End Session
          </button>
        </div>
      </main>

      <style jsx>{`
        .interaction-layout {
          display: grid;
          grid-template-columns: 1fr 380px;
          height: 100vh;
          background: #0a0b0f;
          color: #e0e0e8;
          font-family: 'Inter', -apple-system, sans-serif;
        }
        .panel {
          display: flex;
          flex-direction: column;
          border-right: 1px solid rgba(255,255,255,0.06);
          overflow: hidden;
        }
        .panel-left { }
        .panel-right {
          border-right: none;
          background: linear-gradient(180deg, #0d0e14 0%, #0a0b0f 100%);
        }
        .panel-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 16px 20px;
          border-bottom: 1px solid rgba(255,255,255,0.06);
          background: rgba(255,255,255,0.02);
        }
        .panel-header h3 {
          font-size: 14px;
          font-weight: 600;
          margin: 0;
          color: #a0a0b8;
        }
        .turn-badge {
          font-size: 12px;
          padding: 3px 10px;
          border-radius: 12px;
          background: rgba(99,102,241,0.15);
          color: #818cf8;
          font-weight: 600;
        }
        .timer {
          font-size: 13px;
          font-family: 'JetBrains Mono', monospace;
          color: #6366f1;
          font-weight: 600;
        }
        .chat-container {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .chat-container::-webkit-scrollbar { width: 4px; }
        .chat-container::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
        .chat-input-area {
          padding: 12px 16px;
          border-top: 1px solid rgba(255,255,255,0.06);
          display: flex;
          gap: 8px;
          align-items: flex-end;
          background: rgba(255,255,255,0.02);
        }
        .chat-input-area textarea {
          flex: 1;
          background: rgba(255,255,255,0.04);
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 10px;
          padding: 10px 14px;
          color: #e0e0e8;
          font-size: 14px;
          resize: none;
          outline: none;
          font-family: inherit;
          transition: border-color 0.2s;
        }
        .chat-input-area textarea:focus {
          border-color: rgba(99,102,241,0.5);
        }
        .chat-input-area textarea:disabled {
          opacity: 0.4;
        }
        .btn-send {
          padding: 10px 18px;
          background: linear-gradient(135deg, #6366f1, #8b5cf6);
          color: white;
          border: none;
          border-radius: 10px;
          cursor: pointer;
          font-size: 13px;
          font-weight: 600;
          transition: all 0.2s;
          white-space: nowrap;
        }
        .btn-send:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 4px 16px rgba(99,102,241,0.3);
        }
        .btn-send:disabled { opacity: 0.4; cursor: not-allowed; }
        .session-controls {
          padding: 16px;
          border-top: 1px solid rgba(255,255,255,0.06);
          display: flex;
          gap: 8px;
        }
        .btn-control {
          flex: 1;
          padding: 10px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 13px;
          font-weight: 600;
          transition: all 0.2s;
        }
        .btn-pause {
          background: rgba(251,191,36,0.12);
          color: #fbbf24;
        }
        .btn-resume {
          background: rgba(52,211,153,0.12);
          color: #34d399;
        }
        .btn-end {
          background: rgba(239,68,68,0.12);
          color: #ef4444;
        }
        .btn-control:hover { transform: translateY(-1px); }
        .btn-control:disabled { opacity: 0.4; cursor: not-allowed; }
      `}</style>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
//  Sub-Components
// ═══════════════════════════════════════════════════════════════════

function SetupScreen({ subject, setSubject, department, setDepartment, persona, setPersona, onStart, isLoading }: any) {
  const personas = [
    'Beginner', 'Confused', 'Curious', 'Average', 'Excellent',
    'PracticalLearner', 'ResearchStudent', 'IndustryStudent',
    'ExamOriented', 'SlowLearner', 'AdvancedLearner'
  ];

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #0a0b0f 0%, #1a1b2e 50%, #0a0b0f 100%)',
      fontFamily: "'Inter', sans-serif",
    }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        style={{
          background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: 20, padding: 40, width: 520, backdropFilter: 'blur(20px)',
        }}
      >
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, background: 'linear-gradient(135deg, #6366f1, #a855f7)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          🎓 Teaching Interaction
        </h1>
        <p style={{ color: '#8888a0', marginBottom: 32, fontSize: 14 }}>
          Configure the AI student simulation for faculty teaching assessment.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <label style={{ color: '#a0a0b8', fontSize: 13, fontWeight: 600 }}>
            Subject
            <input value={subject} onChange={e => setSubject(e.target.value)}
              style={{ width: '100%', marginTop: 6, padding: '10px 14px', background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, color: '#e0e0e8', fontSize: 14, outline: 'none' }} />
          </label>
          <label style={{ color: '#a0a0b8', fontSize: 13, fontWeight: 600 }}>
            Department
            <input value={department} onChange={e => setDepartment(e.target.value)}
              style={{ width: '100%', marginTop: 6, padding: '10px 14px', background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, color: '#e0e0e8', fontSize: 14, outline: 'none' }} />
          </label>
          <label style={{ color: '#a0a0b8', fontSize: 13, fontWeight: 600 }}>
            Student Persona
            <select value={persona} onChange={e => setPersona(e.target.value)}
              style={{ width: '100%', marginTop: 6, padding: '10px 14px', background: '#12131a',
                border: '1px solid rgba(255,255,255,0.08)', borderRadius: 10, color: '#e0e0e8', fontSize: 14, outline: 'none' }}>
              {personas.map(p => <option key={p} value={p}>{p.replace(/([A-Z])/g, ' $1').trim()}</option>)}
            </select>
          </label>
        </div>

        <button onClick={onStart} disabled={isLoading}
          style={{
            width: '100%', marginTop: 28, padding: '14px', border: 'none', borderRadius: 12,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white',
            fontSize: 15, fontWeight: 700, cursor: 'pointer', transition: 'all 0.2s',
          }}>
          {isLoading ? '⏳ Starting...' : '🚀 Start Teaching Session'}
        </button>
      </motion.div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isStudent = message.role === 'student';
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        alignSelf: isStudent ? 'flex-start' : 'flex-end',
        maxWidth: '80%',
      }}
    >
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4,
        flexDirection: isStudent ? 'row' : 'row-reverse',
      }}>
        <span style={{ fontSize: 11, color: '#6b6b80' }}>
          {isStudent ? '🎓 Student' : '👨‍🏫 Faculty'}
        </span>
        <span style={{
          fontSize: 10, padding: '1px 6px', borderRadius: 6,
          background: `${BLOOM_COLORS[message.bloomLevel] || '#6366f1'}22`,
          color: BLOOM_COLORS[message.bloomLevel] || '#6366f1',
        }}>
          {message.bloomLevel}
        </span>
      </div>
      <div style={{
        padding: '12px 16px', borderRadius: 14,
        background: isStudent
          ? 'rgba(99,102,241,0.08)'
          : 'rgba(52,211,153,0.08)',
        border: `1px solid ${isStudent ? 'rgba(99,102,241,0.15)' : 'rgba(52,211,153,0.15)'}`,
        fontSize: 14, lineHeight: 1.6, color: '#d0d0e0',
      }}>
        {message.content}
      </div>
    </motion.div>
  );
}

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0 }} animate={{ opacity: 1 }}
      style={{ alignSelf: 'flex-start', padding: '10px 16px', borderRadius: 14,
               background: 'rgba(99,102,241,0.06)', display: 'flex', gap: 4 }}
    >
      {[0, 1, 2].map(i => (
        <motion.span key={i}
          animate={{ opacity: [0.3, 1, 0.3] }}
          transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
          style={{ width: 6, height: 6, borderRadius: '50%', background: '#6366f1', display: 'block' }}
        />
      ))}
    </motion.div>
  );
}

function AnalyticsDashboard({ analytics }: { analytics: AnalyticsSnapshot }) {
  return (
    <div style={{ flex: 1, overflow: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Current Bloom Level */}
      <div style={{ padding: 14, borderRadius: 12, background: 'rgba(255,255,255,0.02)',
                    border: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ fontSize: 11, color: '#6b6b80', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>
          Bloom's Level
        </div>
        <div style={{ display: 'flex', gap: 4 }}>
          {BLOOM_ORDER.map(level => (
            <div key={level} style={{
              flex: 1, padding: '6px 2px', borderRadius: 6, textAlign: 'center', fontSize: 9,
              background: level === analytics.currentBloomLevel
                ? `${BLOOM_COLORS[level]}22` : 'rgba(255,255,255,0.02)',
              color: level === analytics.currentBloomLevel
                ? BLOOM_COLORS[level] : '#4a4a60',
              border: `1px solid ${level === analytics.currentBloomLevel ? `${BLOOM_COLORS[level]}44` : 'transparent'}`,
              fontWeight: level === analytics.currentBloomLevel ? 700 : 400,
            }}>
              {level.slice(0, 3)}
            </div>
          ))}
        </div>
      </div>

      {/* Score Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        <ScoreCard label="Teaching" value={analytics.teachingScore} color="#6366f1" />
        <ScoreCard label="Communication" value={analytics.communicationScore} color="#8b5cf6" />
        <ScoreCard label="Engagement" value={analytics.engagementScore} color="#a855f7" />
        <ScoreCard label="Learning Gain" value={analytics.learningGain} color="#34d399" />
      </div>

      {/* Understanding Meter */}
      <div style={{ padding: 14, borderRadius: 12, background: 'rgba(255,255,255,0.02)',
                    border: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ fontSize: 11, color: '#6b6b80', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>
          Student Understanding
        </div>
        <div style={{ height: 8, borderRadius: 4, background: 'rgba(255,255,255,0.04)', overflow: 'hidden' }}>
          <motion.div
            animate={{ width: `${analytics.understandingEstimate * 100}%` }}
            transition={{ duration: 0.5 }}
            style={{ height: '100%', borderRadius: 4,
                     background: `linear-gradient(90deg, #6366f1, ${analytics.understandingEstimate > 0.7 ? '#34d399' : '#f59e0b'})` }}
          />
        </div>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#d0d0e0', marginTop: 6, textAlign: 'right' }}>
          {(analytics.understandingEstimate * 100).toFixed(0)}%
        </div>
      </div>

      {/* Misconception Tracker */}
      <div style={{ padding: 14, borderRadius: 12, background: 'rgba(255,255,255,0.02)',
                    border: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ fontSize: 11, color: '#6b6b80', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 1 }}>
          Misconceptions
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <MiniStat label="Total" value={analytics.totalMisconceptions} color="#f59e0b" />
          <MiniStat label="Corrected" value={analytics.correctedMisconceptions} color="#34d399" />
          <MiniStat label="Missed" value={analytics.missedMisconceptions} color="#ef4444" />
        </div>
      </div>

      {/* Bloom Distribution */}
      <div style={{ padding: 14, borderRadius: 12, background: 'rgba(255,255,255,0.02)',
                    border: '1px solid rgba(255,255,255,0.06)' }}>
        <div style={{ fontSize: 11, color: '#6b6b80', marginBottom: 10, textTransform: 'uppercase', letterSpacing: 1 }}>
          Bloom Distribution
        </div>
        <div style={{ display: 'flex', gap: 3, alignItems: 'flex-end', height: 50 }}>
          {BLOOM_ORDER.map(level => {
            const count = analytics.bloomDistribution[level] || 0;
            const maxCount = Math.max(1, ...Object.values(analytics.bloomDistribution));
            return (
              <div key={level} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                <motion.div
                  animate={{ height: Math.max(4, (count / maxCount) * 40) }}
                  style={{ width: '100%', borderRadius: 3, background: BLOOM_COLORS[level] + '66' }}
                />
                <span style={{ fontSize: 8, color: '#6b6b80' }}>{level.slice(0, 3)}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Evidence Count */}
      <div style={{ padding: 10, borderRadius: 10, background: 'rgba(99,102,241,0.05)',
                    textAlign: 'center', fontSize: 12, color: '#818cf8' }}>
        📋 {analytics.totalEvidencePackets} evidence packets collected
      </div>
    </div>
  );
}

function ScoreCard({ label, value, color }: { label: string; value: number; color: string }) {
  const pct = Math.round(value * 100);
  return (
    <div style={{
      padding: 12, borderRadius: 10, background: 'rgba(255,255,255,0.02)',
      border: '1px solid rgba(255,255,255,0.06)',
    }}>
      <div style={{ fontSize: 10, color: '#6b6b80', textTransform: 'uppercase', letterSpacing: 0.5 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, color, marginTop: 2 }}>{pct}<span style={{ fontSize: 12 }}>%</span></div>
    </div>
  );
}

function MiniStat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ flex: 1, textAlign: 'center' }}>
      <div style={{ fontSize: 20, fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: 10, color: '#6b6b80' }}>{label}</div>
    </div>
  );
}

function ReportView({ report, onClose }: { report: SessionReport; onClose: () => void }) {
  const pct = (v: number) => `${Math.round(v * 100)}%`;
  return (
    <div style={{
      minHeight: '100vh', padding: 40, background: 'linear-gradient(180deg, #0a0b0f, #12131a)',
      fontFamily: "'Inter', sans-serif", color: '#e0e0e8',
    }}>
      <div style={{ maxWidth: 800, margin: '0 auto' }}>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
            <h1 style={{ fontSize: 28, fontWeight: 700, background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                         WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              📊 Teaching Evaluation Report
            </h1>
            <button onClick={onClose} style={{ padding: '8px 20px', background: 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#a0a0b8', cursor: 'pointer' }}>
              ← Back
            </button>
          </div>

          {/* Overall Score */}
          <div style={{ textAlign: 'center', padding: 40, marginBottom: 24, borderRadius: 16,
                        background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.15)' }}>
            <div style={{ fontSize: 13, color: '#818cf8', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>
              Overall Teaching Effectiveness
            </div>
            <div style={{ fontSize: 64, fontWeight: 800, background: 'linear-gradient(135deg, #6366f1, #34d399)',
                          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              {pct(report.overallTeachingEffectiveness)}
            </div>
            <div style={{ fontSize: 13, color: '#6b6b80', marginTop: 4 }}>
              {report.totalTurns} turns • {report.duration} • {report.personaUsed} persona
            </div>
          </div>

          {/* Score Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12, marginBottom: 24 }}>
            {Object.entries(report.scores).map(([key, val]) => (
              <div key={key} style={{ padding: 16, borderRadius: 12, background: 'rgba(255,255,255,0.02)',
                                      border: '1px solid rgba(255,255,255,0.06)', textAlign: 'center' }}>
                <div style={{ fontSize: 10, color: '#6b6b80', textTransform: 'uppercase' }}>
                  {key.replace(/([A-Z])/g, ' $1').trim()}
                </div>
                <div style={{ fontSize: 28, fontWeight: 700, color: '#6366f1', marginTop: 4 }}>{pct(val)}</div>
              </div>
            ))}
          </div>

          {/* Strengths & Weaknesses */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 24 }}>
            <div style={{ padding: 20, borderRadius: 14, background: 'rgba(52,211,153,0.04)',
                          border: '1px solid rgba(52,211,153,0.12)' }}>
              <h3 style={{ fontSize: 14, color: '#34d399', marginBottom: 12 }}>✅ Strengths</h3>
              {report.strengths.map((s, i) => (
                <div key={i} style={{ fontSize: 13, color: '#b0b0c0', marginBottom: 8, paddingLeft: 12,
                                      borderLeft: '2px solid rgba(52,211,153,0.3)' }}>{s}</div>
              ))}
            </div>
            <div style={{ padding: 20, borderRadius: 14, background: 'rgba(239,68,68,0.04)',
                          border: '1px solid rgba(239,68,68,0.12)' }}>
              <h3 style={{ fontSize: 14, color: '#ef4444', marginBottom: 12 }}>⚠️ Weaknesses</h3>
              {report.weaknesses.map((w, i) => (
                <div key={i} style={{ fontSize: 13, color: '#b0b0c0', marginBottom: 8, paddingLeft: 12,
                                      borderLeft: '2px solid rgba(239,68,68,0.3)' }}>{w}</div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          {report.recommendations.length > 0 && (
            <div style={{ padding: 20, borderRadius: 14, background: 'rgba(99,102,241,0.04)',
                          border: '1px solid rgba(99,102,241,0.12)', marginBottom: 24 }}>
              <h3 style={{ fontSize: 14, color: '#818cf8', marginBottom: 12 }}>💡 Recommendations</h3>
              {report.recommendations.map((r, i) => (
                <div key={i} style={{ fontSize: 13, color: '#b0b0c0', marginBottom: 8, paddingLeft: 12,
                                      borderLeft: '2px solid rgba(99,102,241,0.3)' }}>{r}</div>
              ))}
            </div>
          )}

          {/* Evidence Timeline */}
          {report.evidence.length > 0 && (
            <div style={{ padding: 20, borderRadius: 14, background: 'rgba(255,255,255,0.02)',
                          border: '1px solid rgba(255,255,255,0.06)' }}>
              <h3 style={{ fontSize: 14, color: '#a0a0b8', marginBottom: 12 }}>📋 Evidence Timeline</h3>
              {report.evidence.map((e, i) => (
                <div key={i} style={{ padding: 12, marginBottom: 8, borderRadius: 10,
                                      background: 'rgba(255,255,255,0.02)', fontSize: 13 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ color: '#818cf8' }}>Turn {e.turnNumber} • {e.type}</span>
                    <span style={{ color: '#34d399', fontWeight: 600 }}>{pct(e.score)}</span>
                  </div>
                  <div style={{ color: '#8888a0', fontSize: 12 }}>{e.justification}</div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
