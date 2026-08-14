using FacultyIQ.Domain.Abstractions;

namespace FacultyIQ.Domain.Entities.Interaction;

/// <summary>
/// Defines the simulated student persona that the AI adopts during an interaction session.
/// Each persona drives different questioning patterns, confusion thresholds, and
/// misconception probabilities — creating authentic, varied student behaviors.
/// </summary>
public class StudentPersona : BaseEntity
{
    public PersonaType Type { get; private set; }
    public string Name { get; private set; } = string.Empty;
    public string Description { get; private set; } = string.Empty;

    /// <summary>
    /// Behavioral traits as a comma-separated string (e.g., "asks many questions, needs examples, impatient").
    /// </summary>
    public string BehaviorTraits { get; private set; } = string.Empty;

    /// <summary>
    /// Probability (0.0–1.0) that the student will present a misconception in any given turn.
    /// Higher values simulate students who frequently misunderstand concepts.
    /// </summary>
    public decimal MisconceptionProbability { get; private set; }

    /// <summary>
    /// Threshold (0.0–1.0) for the student's "confusion level" that triggers follow-up questions.
    /// Lower values mean the student asks follow-ups more easily.
    /// </summary>
    public decimal ConfusionThreshold { get; private set; }

    /// <summary>
    /// How aggressively (0.0–1.0) the student asks for clarification, examples, and alternative explanations.
    /// </summary>
    public decimal FollowUpAggressiveness { get; private set; }

    /// <summary>
    /// The style of questions this persona prefers (e.g., "why-based", "example-seeking", "comparison", "practical").
    /// </summary>
    public string QuestionStyle { get; private set; } = string.Empty;

    /// <summary>
    /// The starting Bloom level appropriate for this persona.
    /// </summary>
    public BloomLevel StartingBloomLevel { get; private set; }

    private StudentPersona() { } // EF Core

    public static StudentPersona Create(
        PersonaType type,
        string name,
        string description,
        string behaviorTraits,
        decimal misconceptionProbability,
        decimal confusionThreshold,
        decimal followUpAggressiveness,
        string questionStyle,
        BloomLevel startingBloomLevel)
    {
        return new StudentPersona
        {
            Id = Guid.NewGuid(),
            Type = type,
            Name = name,
            Description = description,
            BehaviorTraits = behaviorTraits,
            MisconceptionProbability = Math.Clamp(misconceptionProbability, 0m, 1m),
            ConfusionThreshold = Math.Clamp(confusionThreshold, 0m, 1m),
            FollowUpAggressiveness = Math.Clamp(followUpAggressiveness, 0m, 1m),
            QuestionStyle = questionStyle,
            StartingBloomLevel = startingBloomLevel
        };
    }

    /// <summary>
    /// Factory method to get predefined persona configurations.
    /// </summary>
    public static StudentPersona GetDefault(PersonaType type)
    {
        return type switch
        {
            PersonaType.Beginner => Create(type, "Beginner Student",
                "A student with minimal prior knowledge who needs fundamental explanations.",
                "needs basics, asks for definitions, requires step-by-step", 0.6m, 0.3m, 0.7m,
                "definition-seeking", BloomLevel.Remember),

            PersonaType.Confused => Create(type, "Confused Student",
                "A student who frequently misunderstands concepts and needs multiple explanations.",
                "mixes up concepts, needs repetition, asks 'I still don't get it'", 0.8m, 0.2m, 0.9m,
                "clarification-seeking", BloomLevel.Remember),

            PersonaType.Curious => Create(type, "Curious Student",
                "An engaged student who asks 'why' and 'how' frequently and seeks deeper understanding.",
                "asks why, seeks connections, wants real-world links, probes deeper", 0.3m, 0.5m, 0.8m,
                "why-based", BloomLevel.Understand),

            PersonaType.Average => Create(type, "Average Student",
                "A typical student who understands basics but needs help with complex topics.",
                "grasps basics, struggles with abstraction, needs examples", 0.4m, 0.5m, 0.5m,
                "example-seeking", BloomLevel.Understand),

            PersonaType.Excellent => Create(type, "Excellent Student",
                "A strong student who challenges faculty with advanced questions.",
                "pushes boundaries, asks edge cases, seeks optimization", 0.1m, 0.7m, 0.6m,
                "challenge-oriented", BloomLevel.Apply),

            PersonaType.PracticalLearner => Create(type, "Practical Learner",
                "A student focused on real-world application and industry relevance.",
                "asks for use cases, wants industry examples, practical-minded", 0.3m, 0.5m, 0.6m,
                "application-focused", BloomLevel.Apply),

            PersonaType.ResearchStudent => Create(type, "Research Student",
                "A student interested in theoretical depth and research implications.",
                "asks about edge cases, wants formal proofs, research-oriented", 0.2m, 0.6m, 0.7m,
                "theory-focused", BloomLevel.Analyze),

            PersonaType.IndustryStudent => Create(type, "Industry Student",
                "A working professional who wants practical, immediately applicable knowledge.",
                "impatient with theory, wants quick solutions, values efficiency", 0.3m, 0.6m, 0.5m,
                "solution-oriented", BloomLevel.Apply),

            PersonaType.ExamOriented => Create(type, "Exam-Oriented Student",
                "A student focused on passing exams, asks about common exam patterns.",
                "wants formulas, asks what's on the test, memorization-focused", 0.5m, 0.4m, 0.4m,
                "pattern-seeking", BloomLevel.Remember),

            PersonaType.SlowLearner => Create(type, "Slow Learner",
                "A student who needs extra time and repetition to understand concepts.",
                "needs repetition, slow pace, asks same question differently", 0.7m, 0.2m, 0.8m,
                "repetition-seeking", BloomLevel.Remember),

            PersonaType.AdvancedLearner => Create(type, "Advanced Learner",
                "A highly capable student who evaluates and creates new solutions.",
                "evaluates approaches, suggests improvements, creates solutions", 0.1m, 0.8m, 0.5m,
                "evaluation-focused", BloomLevel.Evaluate),

            _ => Create(type, "Default Student", "A balanced student persona.",
                "balanced, moderate pace", 0.4m, 0.5m, 0.5m,
                "balanced", BloomLevel.Understand)
        };
    }
}
