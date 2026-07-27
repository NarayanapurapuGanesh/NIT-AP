export interface AgentSessionScore {
  resumeScore: number;
  videoScore: number;
  codingScore: number;
  interactionScore: number;
  overallScore: number;
}

export interface CandidateEvaluationSession {
  id: string;
  candidateName: string;
  candidateEmail: string;
  department: string;
  appliedRank: string;
  createdAt: string;
  scores: AgentSessionScore;
  recommendation: 'Highly Recommended' | 'Recommended' | 'Conditional' | 'Not Recommended';
  summary: string;
  resumeDetails?: {
    highestDegree: string;
    expYears: number;
    skills: string[];
    papersCount: number;
  };
  videoDetails?: {
    clarityScore: number;
    confidenceScore: number;
    pedagogyScore: number;
  };
  codingDetails?: {
    testCasesPassed: string;
    codeQuality: string;
    algoScore: number;
  };
  interactionDetails?: {
    questionsAnswered: number;
    qnaScore: number;
  };
}

const getStorageKey = (email: string) => `facultyiq_sessions_${email.toLowerCase()}`;

export const getUserSessions = (email: string): CandidateEvaluationSession[] => {
  if (!email) return [];
  try {
    const data = localStorage.getItem(getStorageKey(email));
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
};

export const saveUserSession = (email: string, session: CandidateEvaluationSession): CandidateEvaluationSession[] => {
  const currentSessions = getUserSessions(email);
  const updated = [session, ...currentSessions];
  try {
    localStorage.setItem(getStorageKey(email), JSON.stringify(updated));
  } catch {
    // Ignore storage write error
  }
  return updated;
};

export const seedDemoSessions = (email: string): CandidateEvaluationSession[] => {
  const demoSessions: CandidateEvaluationSession[] = [
    {
      id: 'sess_101',
      candidateName: 'Candidate_Dossier_101.pdf',
      candidateEmail: email,
      department: 'Computer Science & Engineering',
      appliedRank: 'Assistant Professor',
      createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
      scores: {
        resumeScore: 94,
        videoScore: 90,
        codingScore: 95,
        interactionScore: 92,
        overallScore: 92.75,
      },
      recommendation: 'Highly Recommended',
      summary: 'High performance across CV resume verification, video presentation, coding efficiency, and committee Q&A session.',
      resumeDetails: {
        highestDegree: 'Ph.D. in Computer Science',
        expYears: 6,
        skills: ['Distributed Systems', 'Kubernetes', 'Go / C++', 'Fault Tolerance'],
        papersCount: 34,
      },
    },
  ];

  try {
    localStorage.setItem(getStorageKey(email), JSON.stringify(demoSessions));
  } catch {
    // Ignore storage error
  }
  return demoSessions;
};

export const clearUserSessions = (email: string) => {
  try {
    localStorage.removeItem(getStorageKey(email));
  } catch {
    // Ignore storage error
  }
};
