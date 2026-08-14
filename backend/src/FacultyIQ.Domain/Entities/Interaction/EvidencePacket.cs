using FacultyIQ.Domain.Abstractions;

namespace FacultyIQ.Domain.Entities.Interaction;

/// <summary>
/// Structured evidence record that links a teaching evaluation score to the exact
/// conversation turn that produced it. This is the core "explainability" requirement —
/// every score must be traceable to evidence.
/// </summary>
public class EvidencePacket : BaseEntity
{
    public Guid SessionId { get; private set; }
    public Guid ConversationTurnId { get; private set; }
    public int TurnNumber { get; private set; }

    /// <summary>
    /// Type of evidence captured (e.g., "concept_clarity", "misconception_correction",
    /// "example_quality", "bloom_progression", "engagement", "communication").
    /// </summary>
    public string EvidenceType { get; private set; } = string.Empty;

    /// <summary>
    /// The specific score for this evidence dimension (0.0–1.0).
    /// </summary>
    public decimal Score { get; private set; }

    /// <summary>
    /// AI-generated justification explaining why this score was assigned.
    /// Enables human reviewers to understand and audit the evaluation.
    /// </summary>
    public string Justification { get; private set; } = string.Empty;

    /// <summary>
    /// The Bloom level at which this evidence was captured.
    /// </summary>
    public BloomLevel BloomLevel { get; private set; }

    /// <summary>
    /// Full metrics as a JSON blob for detailed drill-down.
    /// </summary>
    public string? MetricsJson { get; private set; }

    /// <summary>
    /// Confidence of the AI evaluation (0.0–1.0).
    /// </summary>
    public decimal Confidence { get; private set; }

    public DateTime CreatedAtUtc { get; private set; }

    // Navigation
    public InteractionSession Session { get; private set; } = null!;
    public ConversationTurn ConversationTurn { get; private set; } = null!;

    private EvidencePacket() { } // EF Core

    public static EvidencePacket Create(
        Guid sessionId,
        Guid conversationTurnId,
        int turnNumber,
        string evidenceType,
        decimal score,
        string justification,
        BloomLevel bloomLevel,
        decimal confidence,
        string? metricsJson = null)
    {
        return new EvidencePacket
        {
            Id = Guid.NewGuid(),
            SessionId = sessionId,
            ConversationTurnId = conversationTurnId,
            TurnNumber = turnNumber,
            EvidenceType = evidenceType,
            Score = Math.Clamp(score, 0m, 1m),
            Justification = justification,
            BloomLevel = bloomLevel,
            Confidence = Math.Clamp(confidence, 0m, 1m),
            MetricsJson = metricsJson,
            CreatedAtUtc = DateTime.UtcNow
        };
    }
}
