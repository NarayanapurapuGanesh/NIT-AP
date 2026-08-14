using FacultyIQ.Domain.Abstractions;

namespace FacultyIQ.Domain.Entities.Interaction;

/// <summary>
/// Represents a single message exchange within a teaching interaction session.
/// Each turn captures who spoke, what they said, the current Bloom level,
/// and a snapshot of teaching quality metrics (if evaluated).
/// </summary>
public class ConversationTurn : BaseEntity
{
    public Guid SessionId { get; private set; }
    public int TurnNumber { get; private set; }
    public SpeakerRole Speaker { get; private set; }
    public string Content { get; private set; } = string.Empty;
    public BloomLevel BloomLevel { get; private set; }

    /// <summary>
    /// Teaching metrics snapshot serialized as JSON for this turn.
    /// Only populated for Faculty turns after evaluation.
    /// </summary>
    public string? MetricsSnapshotJson { get; private set; }

    /// <summary>
    /// Estimated student understanding after this turn (0.0–1.0).
    /// Tracks how much the student's comprehension improved.
    /// </summary>
    public decimal? UnderstandingEstimate { get; private set; }

    /// <summary>
    /// The difficulty level active during this turn.
    /// </summary>
    public DifficultyLevel DifficultyLevel { get; private set; }

    public DateTime CreatedAtUtc { get; private set; }

    // Navigation
    public InteractionSession Session { get; private set; } = null!;

    private ConversationTurn() { } // EF Core

    public static ConversationTurn Create(
        Guid sessionId,
        int turnNumber,
        SpeakerRole speaker,
        string content,
        BloomLevel bloomLevel,
        DifficultyLevel difficultyLevel)
    {
        return new ConversationTurn
        {
            Id = Guid.NewGuid(),
            SessionId = sessionId,
            TurnNumber = turnNumber,
            Speaker = speaker,
            Content = content,
            BloomLevel = bloomLevel,
            DifficultyLevel = difficultyLevel,
            CreatedAtUtc = DateTime.UtcNow
        };
    }

    public void SetMetricsSnapshot(string metricsJson, decimal? understandingEstimate)
    {
        MetricsSnapshotJson = metricsJson;
        UnderstandingEstimate = understandingEstimate;
    }
}
