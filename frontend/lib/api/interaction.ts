/**
 * Interaction Intelligence Agent API client.
 * Handles all HTTP communication with the backend InteractionController.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL
  ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/interaction`
  : '/api/v1/interaction';

// ─── Types ──────────────────────────────────────────────────────

export interface StartInteractionRequest {
  candidateApplicationId: string;
  subject: string;
  department: string;
  personaOverride?: string;
  maxTurns?: number;
  facultyContextJson?: string;
}

export interface StartInteractionResponse {
  sessionId: string;
  personaName: string;
  personaType: string;
  openingStudentMessage: string;
  initialBloomLevel: string;
  subject: string;
}

export interface FacultyMessageRequest {
  sessionId: string;
  message: string;
}

export interface StudentResponseResult {
  studentMessage: string;
  turnNumber: number;
  currentBloomLevel: string;
  currentDifficulty: string;
  sessionComplete: boolean;
  analytics: InteractionAnalyticsSnapshot;
}

export interface InteractionAnalyticsSnapshot {
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

export interface InteractionSessionReport {
  sessionId: string;
  candidateApplicationId: string;
  overallTeachingEffectiveness: number;
  scores: {
    teaching: number;
    communication: number;
    engagement: number;
    studentSatisfaction: number;
    learningGain: number;
    bloomCoverage: number;
  };
  bloomDistribution: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  evidence: EvidenceSummary[];
  recommendations: string[];
  confidence: number;
  totalTurns: number;
  duration: string;
  personaUsed: string;
  subject: string;
  department: string;
}

export interface EvidenceSummary {
  turnNumber: number;
  type: string;
  score: number;
  justification: string;
  confidence: number;
}

// ─── API Functions ──────────────────────────────────────────────

export async function startInteractionSession(
  data: StartInteractionRequest
): Promise<StartInteractionResponse> {
  const res = await fetch(`${API_BASE}/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Failed to start interaction session');
  }
  return res.json();
}

export async function sendFacultyMessage(
  data: FacultyMessageRequest
): Promise<StudentResponseResult> {
  const res = await fetch(`${API_BASE}/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Failed to send message');
  }
  return res.json();
}

export async function endInteractionSession(
  sessionId: string
): Promise<InteractionSessionReport> {
  const res = await fetch(`${API_BASE}/end?sessionId=${sessionId}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || 'Failed to end session');
  }
  return res.json();
}

export async function pauseSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/${sessionId}/pause`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to pause session');
}

export async function resumeSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/${sessionId}/resume`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to resume session');
}

export async function getSessionReport(
  sessionId: string
): Promise<InteractionSessionReport> {
  const res = await fetch(`${API_BASE}/${sessionId}/report`);
  if (!res.ok) throw new Error('Failed to get session report');
  return res.json();
}

export async function getSessionAnalytics(
  sessionId: string
): Promise<InteractionAnalyticsSnapshot> {
  const res = await fetch(`${API_BASE}/${sessionId}/analytics`);
  if (!res.ok) throw new Error('Failed to get session analytics');
  return res.json();
}
