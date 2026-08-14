namespace FacultyIQ.Domain.Entities.Interaction;

/// <summary>
/// Value object representing a comprehensive snapshot of teaching quality metrics.
/// Each property is scored from 0.0 to 1.0. Used both per-turn and as session aggregate.
/// Immutable record type — consistent with the EvaluationScores pattern used in Recruitment.
/// </summary>
public record TeachingMetrics
{
    // --- Concept Clarity (Weight: 20%) ---
    public decimal ConceptClarity { get; init; }
    public decimal TechnicalAccuracy { get; init; }
    public decimal Completeness { get; init; }
    public decimal ExplanationSimplicity { get; init; }

    // --- Explanation Quality (Weight: 20%) ---
    public decimal LogicalFlow { get; init; }
    public decimal Depth { get; init; }
    public decimal ExampleQuality { get; init; }
    public decimal AnalogyUsage { get; init; }
    public decimal RealWorldRelevance { get; init; }

    // --- Student Engagement (Weight: 15%) ---
    public decimal QuestionHandling { get; init; }
    public decimal DoubtClarification { get; init; }
    public decimal AdaptiveTeaching { get; init; }
    public decimal InteractiveStyle { get; init; }

    // --- Communication (Weight: 10%) ---
    public decimal Grammar { get; init; }
    public decimal Fluency { get; init; }
    public decimal Vocabulary { get; init; }
    public decimal Professionalism { get; init; }

    // --- Higher-Order Thinking Encouragement ---
    public decimal CriticalThinkingEncouragement { get; init; }
    public decimal ProblemSolvingGuidance { get; init; }

    public static TeachingMetrics Empty => new();

    /// <summary>
    /// Calculates the weighted Concept Clarity sub-score.
    /// </summary>
    public decimal GetConceptClarityScore()
    {
        return (ConceptClarity + TechnicalAccuracy + Completeness + ExplanationSimplicity) / 4m;
    }

    /// <summary>
    /// Calculates the weighted Explanation Quality sub-score.
    /// </summary>
    public decimal GetExplanationQualityScore()
    {
        return (LogicalFlow + Depth + ExampleQuality + AnalogyUsage + RealWorldRelevance) / 5m;
    }

    /// <summary>
    /// Calculates the weighted Student Engagement sub-score.
    /// </summary>
    public decimal GetEngagementScore()
    {
        return (QuestionHandling + DoubtClarification + AdaptiveTeaching + InteractiveStyle) / 4m;
    }

    /// <summary>
    /// Calculates the weighted Communication sub-score.
    /// </summary>
    public decimal GetCommunicationScore()
    {
        return (Grammar + Fluency + Vocabulary + Professionalism) / 4m;
    }

    /// <summary>
    /// Calculates the overall weighted teaching score across all dimensions.
    /// Weights: Concept Clarity 20%, Explanation Quality 20%, Engagement 15%,
    /// Communication 10%, Higher-Order Thinking 10%, remainder from individual metrics.
    /// </summary>
    public decimal GetOverallScore()
    {
        var conceptClarity = GetConceptClarityScore() * 0.20m;
        var explanationQuality = GetExplanationQualityScore() * 0.20m;
        var engagement = GetEngagementScore() * 0.15m;
        var communication = GetCommunicationScore() * 0.10m;
        var higherOrder = ((CriticalThinkingEncouragement + ProblemSolvingGuidance) / 2m) * 0.10m;

        // Remaining 25% distributed across key individual metrics
        var keyMetrics = (ConceptClarity + ExampleQuality + DoubtClarification +
                          AdaptiveTeaching + TechnicalAccuracy) / 5m * 0.25m;

        return conceptClarity + explanationQuality + engagement + communication +
               higherOrder + keyMetrics;
    }
}
