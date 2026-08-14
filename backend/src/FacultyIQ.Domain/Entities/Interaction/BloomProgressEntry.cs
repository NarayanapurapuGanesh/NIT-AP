using FacultyIQ.Domain.Abstractions;

namespace FacultyIQ.Domain.Entities.Interaction;

/// <summary>
/// Tracks Bloom's Taxonomy level transitions throughout the interaction session.
/// Each entry records a progression (or regression) in cognitive complexity,
/// enabling visualization of teaching depth over time.
/// </summary>
public class BloomProgressEntry : BaseEntity
{
    public Guid SessionId { get; private set; }
    public int TurnNumber { get; private set; }
    public BloomLevel PreviousLevel { get; private set; }
    public BloomLevel CurrentLevel { get; private set; }

    /// <summary>
    /// The topic being discussed when the Bloom level changed.
    /// </summary>
    public string Topic { get; private set; } = string.Empty;

    /// <summary>
    /// Direction of progression: "advanced", "maintained", "regressed".
    /// </summary>
    public string ProgressDirection { get; private set; } = string.Empty;

    /// <summary>
    /// Reason for the transition (e.g., "Faculty introduced application example",
    /// "Student asked for evaluation of approaches").
    /// </summary>
    public string? TransitionReason { get; private set; }

    public DateTime CreatedAtUtc { get; private set; }

    // Navigation
    public InteractionSession Session { get; private set; } = null!;

    private BloomProgressEntry() { } // EF Core

    public static BloomProgressEntry Create(
        Guid sessionId,
        int turnNumber,
        BloomLevel previousLevel,
        BloomLevel currentLevel,
        string topic,
        string? transitionReason = null)
    {
        var direction = currentLevel > previousLevel ? "advanced"
                       : currentLevel < previousLevel ? "regressed"
                       : "maintained";

        return new BloomProgressEntry
        {
            Id = Guid.NewGuid(),
            SessionId = sessionId,
            TurnNumber = turnNumber,
            PreviousLevel = previousLevel,
            CurrentLevel = currentLevel,
            Topic = topic,
            ProgressDirection = direction,
            TransitionReason = transitionReason,
            CreatedAtUtc = DateTime.UtcNow
        };
    }
}
