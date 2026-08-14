using FacultyIQ.Domain.Abstractions;
using FacultyIQ.Domain.Entities.Interaction;

namespace FacultyIQ.Domain.Events.Interaction;

/// <summary>
/// Raised when a new teaching interaction session is started.
/// </summary>
public record InteractionSessionStartedEvent(
    Guid SessionId,
    Guid CandidateApplicationId,
    PersonaType PersonaType,
    string Subject,
    string Department
) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredOnUtc { get; } = DateTime.UtcNow;
}

/// <summary>
/// Raised when a teaching interaction session is completed (all turns exhausted or manually ended).
/// </summary>
public record InteractionSessionCompletedEvent(
    Guid SessionId,
    int TotalTurns,
    BloomLevel HighestBloomReached,
    TimeSpan? Duration
) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredOnUtc { get; } = DateTime.UtcNow;
}

/// <summary>
/// Raised when a teaching evidence packet is generated from an evaluation.
/// </summary>
public record TeachingEvidenceGeneratedEvent(
    Guid SessionId,
    Guid EvidencePacketId,
    string EvidenceType,
    decimal Score,
    decimal Confidence
) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredOnUtc { get; } = DateTime.UtcNow;
}

/// <summary>
/// Raised when the Bloom taxonomy level advances during a session.
/// </summary>
public record BloomLevelAdvancedEvent(
    Guid SessionId,
    BloomLevel PreviousLevel,
    BloomLevel NewLevel,
    string Topic,
    int TurnNumber
) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredOnUtc { get; } = DateTime.UtcNow;
}

/// <summary>
/// Raised when the final teaching evaluation scores are set on a session.
/// </summary>
public record InteractionEvaluatedEvent(
    Guid SessionId,
    decimal OverallEffectivenessScore,
    decimal TeachingScore,
    decimal CommunicationScore,
    decimal EngagementScore,
    decimal Confidence
) : IDomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredOnUtc { get; } = DateTime.UtcNow;
}
