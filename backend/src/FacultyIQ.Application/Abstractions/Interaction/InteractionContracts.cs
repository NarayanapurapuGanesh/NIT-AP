using FacultyIQ.Domain.Entities.Interaction;

namespace FacultyIQ.Application.Abstractions.Interaction;

// ═══════════════════════════════════════════════════════════════════
//  DTOs — Data Transfer Objects for the Interaction Agent pipeline
// ═══════════════════════════════════════════════════════════════════

/// <summary>Request to start a new interaction session.</summary>
public record StartInteractionRequest(
    Guid CandidateApplicationId,
    string Subject,
    string Department,
    PersonaType? PersonaOverride = null,
    int MaxTurns = 20,
    string? FacultyContextJson = null
);

/// <summary>Response after starting a session, includes the first AI student message.</summary>
public record StartInteractionResponse(
    Guid SessionId,
    string PersonaName,
    PersonaType PersonaType,
    string OpeningStudentMessage,
    BloomLevel InitialBloomLevel,
    string Subject
);

/// <summary>Faculty sends a message during the session.</summary>
public record FacultyMessageRequest(
    Guid SessionId,
    string Message
);

/// <summary>AI student response plus real-time analytics update.</summary>
public record StudentResponseResult(
    string StudentMessage,
    int TurnNumber,
    BloomLevel CurrentBloomLevel,
    DifficultyLevel CurrentDifficulty,
    bool SessionComplete,
    InteractionAnalyticsSnapshot Analytics
);

/// <summary>Live analytics snapshot sent to the dashboard after each turn.</summary>
public record InteractionAnalyticsSnapshot(
    // Core Scores
    decimal TeachingScore,
    decimal CommunicationScore,
    decimal EngagementScore,
    decimal StudentSatisfaction,
    decimal LearningGain,

    // Progress
    BloomLevel CurrentBloomLevel,
    int TurnNumber,
    int MaxTurns,
    string CurrentTopic,

    // Bloom Distribution
    Dictionary<string, int> BloomDistribution,

    // Misconceptions
    int TotalMisconceptions,
    int CorrectedMisconceptions,
    int MissedMisconceptions,

    // Evidence
    int TotalEvidencePackets,

    // Estimated Understanding
    decimal UnderstandingEstimate
);

/// <summary>Full session report returned after evaluation.</summary>
public record InteractionSessionReport(
    Guid SessionId,
    Guid CandidateApplicationId,
    decimal OverallTeachingEffectiveness,
    InteractionScores Scores,
    Dictionary<string, int> BloomDistribution,
    List<string> Strengths,
    List<string> Weaknesses,
    List<EvidenceSummary> Evidence,
    List<string> Recommendations,
    decimal Confidence,
    int TotalTurns,
    string Duration,
    string PersonaUsed,
    string Subject,
    string Department
);

/// <summary>Detailed score breakdown.</summary>
public record InteractionScores(
    decimal Teaching,
    decimal Communication,
    decimal Engagement,
    decimal StudentSatisfaction,
    decimal LearningGain,
    decimal BloomCoverage
);

/// <summary>Evidence summary for the report.</summary>
public record EvidenceSummary(
    int TurnNumber,
    string Type,
    decimal Score,
    string Justification,
    decimal Confidence
);

/// <summary>Request body sent to the Python AI service.</summary>
public record AIInteractionRequest(
    string SessionId,
    string FacultyMessage,
    string PersonaType,
    string Subject,
    string Department,
    int TurnNumber,
    int MaxTurns,
    string CurrentBloomLevel,
    string CurrentDifficulty,
    List<ConversationMessage> ConversationHistory,
    List<ActiveMisconception> ActiveMisconceptions,
    string? FacultyContextJson
);

/// <summary>Simplified conversation message for AI context.</summary>
public record ConversationMessage(
    string Role,
    string Content,
    int TurnNumber
);

/// <summary>Active misconception state for AI awareness.</summary>
public record ActiveMisconception(
    string MisconceptionText,
    string CorrectConcept,
    string Status
);

/// <summary>Response from the Python AI service.</summary>
public record AIInteractionResponse(
    string StudentMessage,
    string CurrentBloomLevel,
    string? NewBloomLevel,
    string? BloomTransitionReason,
    string CurrentTopic,
    AITeachingEvaluation? Evaluation,
    AIMisconception? NewMisconception,
    AIMisconceptionCorrection? MisconceptionCorrection,
    decimal UnderstandingEstimate,
    bool ShouldEndSession,
    string? EndSessionReason
);

/// <summary>AI's evaluation of the faculty's teaching for this turn.</summary>
public record AITeachingEvaluation(
    decimal ConceptClarity,
    decimal TechnicalAccuracy,
    decimal LogicalFlow,
    decimal ExplanationSimplicity,
    decimal Depth,
    decimal ExampleQuality,
    decimal AnalogyUsage,
    decimal RealWorldRelevance,
    decimal QuestionHandling,
    decimal DoubtClarification,
    decimal AdaptiveTeaching,
    decimal Grammar,
    decimal Fluency,
    decimal Vocabulary,
    decimal Professionalism,
    decimal CriticalThinkingEncouragement,
    string EvidenceJustification,
    decimal Confidence
);

/// <summary>New misconception to present (from AI).</summary>
public record AIMisconception(
    string MisconceptionText,
    string CorrectConcept,
    string SubjectCategory
);

/// <summary>AI's assessment of how faculty corrected a misconception.</summary>
public record AIMisconceptionCorrection(
    string MisconceptionText,
    string CorrectionText,
    decimal CorrectionQuality,
    bool FullyCorrected
);
