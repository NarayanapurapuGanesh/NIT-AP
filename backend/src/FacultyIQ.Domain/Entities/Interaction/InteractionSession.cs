using FacultyIQ.Domain.Abstractions;

namespace FacultyIQ.Domain.Entities.Interaction;

/// <summary>
/// Root aggregate for the teaching interaction session.
/// Manages the entire lifecycle: Created → Active → (Paused ↔ Active) → Completed → Evaluated.
/// Links to the CandidateApplication and holds all child entities (turns, evidence, bloom, misconceptions).
/// </summary>
public class InteractionSession : AuditableEntity, ISoftDelete
{
    public Guid CandidateApplicationId { get; private set; }

    // --- Session Configuration ---
    public PersonaType PersonaType { get; private set; }
    public string Subject { get; private set; } = string.Empty;
    public string Department { get; private set; } = string.Empty;
    public SessionStatus Status { get; private set; }

    // --- Progress Tracking ---
    public BloomLevel CurrentBloomLevel { get; private set; }
    public int TurnCount { get; private set; }
    public int MaxTurns { get; private set; }
    public DifficultyLevel CurrentDifficulty { get; private set; }

    // --- Faculty Context (serialized JSON from resume, video, coding results) ---
    public string? FacultyContextJson { get; private set; }

    // --- Final Scores (populated after evaluation) ---
    public decimal? TeachingScore { get; private set; }
    public decimal? CommunicationScore { get; private set; }
    public decimal? EngagementScore { get; private set; }
    public decimal? StudentSatisfactionScore { get; private set; }
    public decimal? LearningGainScore { get; private set; }
    public decimal? BloomCoverageScore { get; private set; }
    public decimal? OverallEffectivenessScore { get; private set; }
    public decimal? Confidence { get; private set; }

    // --- Final Report (serialized JSON) ---
    public string? FinalReportJson { get; private set; }
    public string? StrengthsJson { get; private set; }
    public string? WeaknessesJson { get; private set; }
    public string? RecommendationsJson { get; private set; }

    // --- Timestamps ---
    public DateTime? StartedAtUtc { get; private set; }
    public DateTime? PausedAtUtc { get; private set; }
    public DateTime? CompletedAtUtc { get; private set; }
    public TimeSpan? TotalDuration { get; private set; }

    // --- Soft Delete ---
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAtUtc { get; set; }
    public string? DeletedBy { get; set; }

    // --- Navigation ---
    private readonly List<ConversationTurn> _conversationTurns = new();
    public IReadOnlyCollection<ConversationTurn> ConversationTurns => _conversationTurns.AsReadOnly();

    private readonly List<EvidencePacket> _evidencePackets = new();
    public IReadOnlyCollection<EvidencePacket> EvidencePackets => _evidencePackets.AsReadOnly();

    private readonly List<BloomProgressEntry> _bloomProgress = new();
    public IReadOnlyCollection<BloomProgressEntry> BloomProgress => _bloomProgress.AsReadOnly();

    private readonly List<MisconceptionRecord> _misconceptions = new();
    public IReadOnlyCollection<MisconceptionRecord> Misconceptions => _misconceptions.AsReadOnly();

    private InteractionSession() { } // EF Core

    /// <summary>
    /// Factory method to create a new interaction session.
    /// </summary>
    public static InteractionSession Create(
        Guid candidateApplicationId,
        PersonaType personaType,
        string subject,
        string department,
        int maxTurns = 20,
        string? facultyContextJson = null)
    {
        var session = new InteractionSession
        {
            Id = Guid.NewGuid(),
            CandidateApplicationId = candidateApplicationId,
            PersonaType = personaType,
            Subject = subject,
            Department = department,
            Status = SessionStatus.Created,
            CurrentBloomLevel = BloomLevel.Remember,
            CurrentDifficulty = DifficultyLevel.Foundational,
            TurnCount = 0,
            MaxTurns = maxTurns,
            FacultyContextJson = facultyContextJson
        };

        return session;
    }

    /// <summary>
    /// Transitions the session to Active and records the start time.
    /// </summary>
    public void Start()
    {
        if (Status != SessionStatus.Created)
            throw new InvalidOperationException($"Cannot start session in {Status} state.");

        Status = SessionStatus.Active;
        StartedAtUtc = DateTime.UtcNow;
    }

    /// <summary>
    /// Records a new conversation turn and increments the turn counter.
    /// </summary>
    public ConversationTurn AddTurn(SpeakerRole speaker, string content)
    {
        if (Status != SessionStatus.Active)
            throw new InvalidOperationException($"Cannot add turn in {Status} state.");

        TurnCount++;
        var turn = ConversationTurn.Create(Id, TurnCount, speaker, content, CurrentBloomLevel, CurrentDifficulty);
        _conversationTurns.Add(turn);
        return turn;
    }

    /// <summary>
    /// Records a Bloom level change.
    /// </summary>
    public void AdvanceBloomLevel(BloomLevel newLevel, string topic, string? reason = null)
    {
        var entry = BloomProgressEntry.Create(Id, TurnCount, CurrentBloomLevel, newLevel, topic, reason);
        _bloomProgress.Add(entry);
        CurrentBloomLevel = newLevel;

        // Adjust difficulty alongside Bloom level
        CurrentDifficulty = newLevel switch
        {
            BloomLevel.Remember or BloomLevel.Understand => DifficultyLevel.Foundational,
            BloomLevel.Apply => DifficultyLevel.Intermediate,
            BloomLevel.Analyze => DifficultyLevel.Advanced,
            BloomLevel.Evaluate or BloomLevel.Create => DifficultyLevel.Expert,
            _ => CurrentDifficulty
        };
    }

    /// <summary>
    /// Records a misconception presented by the AI student.
    /// </summary>
    public MisconceptionRecord AddMisconception(string misconceptionText, string correctConcept, string subjectCategory)
    {
        var record = MisconceptionRecord.Create(Id, TurnCount, misconceptionText, correctConcept, subjectCategory);
        _misconceptions.Add(record);
        return record;
    }

    /// <summary>
    /// Adds an evidence packet linking an evaluation to a specific turn.
    /// </summary>
    public EvidencePacket AddEvidence(
        Guid conversationTurnId,
        string evidenceType,
        decimal score,
        string justification,
        decimal confidence,
        string? metricsJson = null)
    {
        var packet = EvidencePacket.Create(
            Id, conversationTurnId, TurnCount, evidenceType, score,
            justification, CurrentBloomLevel, confidence, metricsJson);
        _evidencePackets.Add(packet);
        return packet;
    }

    /// <summary>
    /// Pauses the session, recording the pause time.
    /// </summary>
    public void Pause()
    {
        if (Status != SessionStatus.Active)
            throw new InvalidOperationException($"Cannot pause session in {Status} state.");

        Status = SessionStatus.Paused;
        PausedAtUtc = DateTime.UtcNow;
    }

    /// <summary>
    /// Resumes the session from a paused state.
    /// </summary>
    public void Resume()
    {
        if (Status != SessionStatus.Paused)
            throw new InvalidOperationException($"Cannot resume session in {Status} state.");

        Status = SessionStatus.Active;
        PausedAtUtc = null;
    }

    /// <summary>
    /// Completes the session, calculates duration.
    /// </summary>
    public void Complete()
    {
        if (Status != SessionStatus.Active && Status != SessionStatus.Paused)
            throw new InvalidOperationException($"Cannot complete session in {Status} state.");

        Status = SessionStatus.Completed;
        CompletedAtUtc = DateTime.UtcNow;

        if (StartedAtUtc.HasValue)
            TotalDuration = CompletedAtUtc.Value - StartedAtUtc.Value;
    }

    /// <summary>
    /// Marks the session as timed out.
    /// </summary>
    public void TimeOut()
    {
        Status = SessionStatus.TimedOut;
        CompletedAtUtc = DateTime.UtcNow;

        if (StartedAtUtc.HasValue)
            TotalDuration = CompletedAtUtc.Value - StartedAtUtc.Value;
    }

    /// <summary>
    /// Records the final evaluation scores and report.
    /// </summary>
    public void SetEvaluationResults(
        decimal teachingScore,
        decimal communicationScore,
        decimal engagementScore,
        decimal studentSatisfactionScore,
        decimal learningGainScore,
        decimal bloomCoverageScore,
        decimal overallEffectivenessScore,
        decimal confidence,
        string finalReportJson,
        string strengthsJson,
        string weaknessesJson,
        string recommendationsJson)
    {
        if (Status != SessionStatus.Completed)
            throw new InvalidOperationException($"Cannot set evaluation results in {Status} state.");

        TeachingScore = Math.Clamp(teachingScore, 0m, 1m);
        CommunicationScore = Math.Clamp(communicationScore, 0m, 1m);
        EngagementScore = Math.Clamp(engagementScore, 0m, 1m);
        StudentSatisfactionScore = Math.Clamp(studentSatisfactionScore, 0m, 1m);
        LearningGainScore = Math.Clamp(learningGainScore, 0m, 1m);
        BloomCoverageScore = Math.Clamp(bloomCoverageScore, 0m, 1m);
        OverallEffectivenessScore = Math.Clamp(overallEffectivenessScore, 0m, 1m);
        Confidence = Math.Clamp(confidence, 0m, 1m);
        FinalReportJson = finalReportJson;
        StrengthsJson = strengthsJson;
        WeaknessesJson = weaknessesJson;
        RecommendationsJson = recommendationsJson;

        Status = SessionStatus.Evaluated;
    }

    /// <summary>
    /// Checks if the session has reached its turn limit.
    /// </summary>
    public bool HasReachedTurnLimit() => TurnCount >= MaxTurns;
}
