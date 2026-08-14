using FacultyIQ.Domain.Abstractions;

namespace FacultyIQ.Domain.Entities.Interaction;

/// <summary>
/// Records a misconception that the AI student presented during the interaction,
/// tracking whether the faculty identified it, corrected it, and the quality of the correction.
/// This is a critical signal for teaching effectiveness — great teachers proactively
/// detect and address student misunderstandings.
/// </summary>
public class MisconceptionRecord : BaseEntity
{
    public Guid SessionId { get; private set; }

    /// <summary>
    /// The turn number where the misconception was first presented by the AI student.
    /// </summary>
    public int TurnPresented { get; private set; }

    /// <summary>
    /// The turn number where the faculty corrected the misconception (null if not corrected).
    /// </summary>
    public int? TurnCorrected { get; private set; }

    /// <summary>
    /// The misconception text as presented by the AI student.
    /// (e.g., "So inheritance and polymorphism are the same thing?")
    /// </summary>
    public string MisconceptionText { get; private set; } = string.Empty;

    /// <summary>
    /// The correct concept that the misconception relates to.
    /// (e.g., "Polymorphism vs Inheritance distinction")
    /// </summary>
    public string CorrectConcept { get; private set; } = string.Empty;

    /// <summary>
    /// The faculty's correction text (null if missed).
    /// </summary>
    public string? CorrectionText { get; private set; }

    /// <summary>
    /// Current status of the misconception lifecycle.
    /// </summary>
    public MisconceptionStatus Status { get; private set; }

    /// <summary>
    /// Quality score of the correction (0.0–1.0), null if not corrected.
    /// Evaluates whether the correction was clear, accurate, and helpful.
    /// </summary>
    public decimal? CorrectionQuality { get; private set; }

    /// <summary>
    /// Subject category (e.g., "OOP", "Data Structures", "Algorithms").
    /// </summary>
    public string SubjectCategory { get; private set; } = string.Empty;

    public DateTime CreatedAtUtc { get; private set; }

    // Navigation
    public InteractionSession Session { get; private set; } = null!;

    private MisconceptionRecord() { } // EF Core

    public static MisconceptionRecord Create(
        Guid sessionId,
        int turnPresented,
        string misconceptionText,
        string correctConcept,
        string subjectCategory)
    {
        return new MisconceptionRecord
        {
            Id = Guid.NewGuid(),
            SessionId = sessionId,
            TurnPresented = turnPresented,
            MisconceptionText = misconceptionText,
            CorrectConcept = correctConcept,
            SubjectCategory = subjectCategory,
            Status = MisconceptionStatus.Presented,
            CreatedAtUtc = DateTime.UtcNow
        };
    }

    public void MarkIdentified()
    {
        if (Status == MisconceptionStatus.Presented)
            Status = MisconceptionStatus.Identified;
    }

    public void MarkCorrected(int turnCorrected, string correctionText, decimal correctionQuality)
    {
        TurnCorrected = turnCorrected;
        CorrectionText = correctionText;
        CorrectionQuality = Math.Clamp(correctionQuality, 0m, 1m);
        Status = MisconceptionStatus.Corrected;
    }

    public void MarkPartiallyCorrected(int turnCorrected, string correctionText, decimal correctionQuality)
    {
        TurnCorrected = turnCorrected;
        CorrectionText = correctionText;
        CorrectionQuality = Math.Clamp(correctionQuality, 0m, 1m);
        Status = MisconceptionStatus.PartiallyCorrected;
    }

    public void MarkMissed()
    {
        Status = MisconceptionStatus.Missed;
        CorrectionQuality = 0m;
    }
}
