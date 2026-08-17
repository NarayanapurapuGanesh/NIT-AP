/**
 * Teaching Interaction Agent API Client.
 * Communicates with the FastAPI Interaction Agent via Next.js rewrites (/api/interaction/*).
 */

const API_BASE = '/api/interaction';

// ─── Types ──────────────────────────────────────────────────────

export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  ollama: string;
  student_model: string;
  evaluator_model: string;
  student_model_available: boolean;
  evaluator_model_available: boolean;
}

export interface CreateSessionRequest {
  candidate_id?: string;
  subject: string;
  department: string;
  persona_type: string;
  max_turns?: number;
}

export interface CreateSessionResponse {
  session_id: string;
  status: string;
  persona_type: string;
  subject: string;
  department: string;
  opening_message: string;
  current_bloom_level: string;
  max_turns: number;
}

export interface FacultyRespondRequest {
  message: string;
}

export interface FacultyRespondResponse {
  student_message: string;
  turn_number: number;
  current_bloom_level: string;
  session_complete: boolean;
  analytics: InteractionAnalyticsSnapshot;
}

export interface SessionStateResponse {
  session_id: string;
  status: string;
  subject: string;
  department: string;
  persona_type: string;
  current_turn: number;
  max_turns: number;
  current_bloom_level: string;
  understanding_estimate: number;
  conversation: Array<{
    turn_number: number;
    speaker: 'Student' | 'Faculty' | 'System';
    message: string;
    bloom_level: string;
    timestamp: string;
  }>;
  analytics: InteractionAnalyticsSnapshot;
}

export interface InteractionAnalyticsSnapshot {
  teaching_score: number;
  communication_score: number;
  engagement_score: number;
  student_satisfaction: number;
  learning_gain: number;
  current_bloom_level: string;
  turn_number: number;
  max_turns: number;
  current_topic: string;
  bloom_distribution: Record<string, number>;
  total_misconceptions: number;
  corrected_misconceptions: number;
  missed_misconceptions: number;
  total_evidence_packets: number;
  understanding_estimate: number;
  concepts_explored: number;
}

export interface EvidencePacket {
  turn_number: number;
  type: string;
  score: number;
  justification: string;
  confidence: number;
  bloom_level: string;
}

export interface TeachingScores {
  technical_accuracy: number;
  concept_clarity: number;
  doubt_resolution: number;
  pedagogical_adaptability: number;
  explanation_structure: number;
  example_quality: number;
  bloom_depth: number;
  misconception_handling: number;
}

export interface InteractionSessionReport {
  session_id: string;
  overall_score: number;
  recommendation: string;
  scores: TeachingScores;
  bloom_profile: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  evidence: EvidencePacket[];
  improvement_areas: string[];
  confidence: number;
  total_turns: number;
  duration: string;
  persona_used: string;
  subject: string;
  department: string;
}

// ─── API Methods ────────────────────────────────────────────────

export async function checkInteractionHealth(): Promise<HealthCheckResponse> {
  const res = await fetch(`${API_BASE}/health`, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error('Health check endpoint unavailable');
  }
  return res.json();
}

export async function startInteractionSession(
  data: CreateSessionRequest
): Promise<CreateSessionResponse> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      candidate_id: data.candidate_id || 'candidate_default',
      subject: data.subject,
      department: data.department,
      persona_type: data.persona_type,
      max_turns: data.max_turns || 12,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData.detail?.message || errorData.detail?.error || errorData.message || 'Failed to start session';
    throw new Error(message);
  }
  return res.json();
}

export async function sendFacultyMessage(
  sessionId: string,
  data: FacultyRespondRequest
): Promise<FacultyRespondResponse> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/respond`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData.detail?.message || errorData.detail || 'Failed to process faculty response';
    throw new Error(message);
  }
  return res.json();
}

export async function getSessionState(sessionId: string): Promise<SessionStateResponse> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error('Failed to retrieve session');
  }
  return res.json();
}

export async function pauseSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/pause`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to pause session');
}

export async function resumeSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/resume`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to resume session');
}

export async function endInteractionSession(sessionId: string): Promise<InteractionSessionReport> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/end`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message = errorData.detail?.message || errorData.detail || 'Failed to end session';
    throw new Error(message);
  }
  return res.json();
}

export async function getSessionReport(sessionId: string): Promise<InteractionSessionReport> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/report`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to get session report');
  return res.json();
}
