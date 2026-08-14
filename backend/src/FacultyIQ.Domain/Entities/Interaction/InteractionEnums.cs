namespace FacultyIQ.Domain.Entities.Interaction;

/// <summary>
/// Lifecycle states of a teaching interaction session.
/// Follows a strict state machine: Created → Active → (Paused ↔ Active) → Completed → Evaluated.
/// </summary>
public enum SessionStatus
{
    Created = 0,
    Active = 1,
    Paused = 2,
    Completed = 3,
    Evaluated = 4,
    TimedOut = 5,
    Cancelled = 6
}

/// <summary>
/// Bloom's Taxonomy cognitive levels, ordered from lowest to highest order thinking.
/// Used to track the progression of teaching complexity throughout a session.
/// </summary>
public enum BloomLevel
{
    Remember = 1,
    Understand = 2,
    Apply = 3,
    Analyze = 4,
    Evaluate = 5,
    Create = 6
}

/// <summary>
/// Defines the simulated student personality the AI adopts during the interaction.
/// Each persona drives different questioning patterns, confusion thresholds, and misconception probabilities.
/// </summary>
public enum PersonaType
{
    Beginner = 0,
    Average = 1,
    Excellent = 2,
    Confused = 3,
    Curious = 4,
    PracticalLearner = 5,
    ResearchStudent = 6,
    IndustryStudent = 7,
    ExamOriented = 8,
    SlowLearner = 9,
    AdvancedLearner = 10
}

/// <summary>
/// Identifies who is speaking in a conversation turn.
/// </summary>
public enum SpeakerRole
{
    Student = 0,
    Faculty = 1,
    System = 2
}

/// <summary>
/// Tracks the lifecycle of a misconception presented by the AI student.
/// </summary>
public enum MisconceptionStatus
{
    Presented = 0,
    Identified = 1,
    Corrected = 2,
    Missed = 3,
    PartiallyCorrected = 4
}

/// <summary>
/// Adaptive difficulty level used by the Question Planning Engine.
/// </summary>
public enum DifficultyLevel
{
    Foundational = 0,
    Intermediate = 1,
    Advanced = 2,
    Expert = 3
}
