const API_BASE = "/api/coding";

export interface SessionResponse {
  session_id: string;
  status: string;
  candidate_name: string;
  programming_language: string;
  difficulty: string;
  questions_answered: number; // <-- Fixed
  max_questions: number;
  total_score: number;
  started_at: string;
}

export interface TestCase {
  input: string;
  expected_output: string;
  is_hidden: boolean;
  is_stress: boolean;
  is_edge_case: boolean;
  description: string;
  time_limit_ms: number;
}

export interface QuestionResponse {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  bloom_level: string;
  tags: string[];
  constraints: string;
  expected_time_complexity: string;
  expected_space_complexity: string;
  starter_code: Record<string, string>;
  hints: string[];
  public_test_cases: TestCase[];
  is_debugging: boolean;
  buggy_code: Record<string, string>;
  bug_description: string;
}

export interface RunCodeResponse {
  status: string;
  stdout: string;
  stderr: string;
  execution_time_ms: number;
  exit_code: number;
}

export interface SubmitResponse {
  submission_id: string;
  session_status: string;
  overall_score: number;
  problem_solving_score: number;
  correctness_score: number;
  complexity_score: number;
  quality_score: number;
  test_results: {
    total: number;
    passed: number;
    failed: number;
    pass_rate: number;
    results: unknown[];
  };
  complexity_analysis: Record<string, unknown>;
  static_analysis: Record<string, unknown>;
}

export interface CompleteSessionResponse {
  status: string;
  message: string;
  report: Record<string, unknown>;
}

export async function startSession(data: Record<string, unknown>): Promise<SessionResponse> {
  const res = await fetch(`${API_BASE}/session/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to start session");
  return res.json();
}

export async function getSession(sessionId: string): Promise<SessionResponse> {
  const res = await fetch(`${API_BASE}/session/${sessionId}`);
  if (!res.ok) throw new Error("Failed to get session");
  return res.json();
}

export async function completeSession(sessionId: string): Promise<CompleteSessionResponse> {
  const res = await fetch(`${API_BASE}/session/${sessionId}/complete`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to complete session");
  return res.json();
}

export async function getNextQuestion(sessionId: string): Promise<QuestionResponse> {
  const res = await fetch(`${API_BASE}/question/next`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) throw new Error("No more questions available or failed to fetch");
  return res.json();
}

export async function runCode(data: {
  source_code: string;
  language: string;
  stdin: string;
}): Promise<RunCodeResponse> {
  const res = await fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to run code");
  return res.json();
}

export async function submitCode(data: {
  session_id: string;
  question_id: string;
  source_code: string;
  language: string;
}): Promise<SubmitResponse> {
  const res = await fetch(`${API_BASE}/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to submit code");
  return res.json();
}
