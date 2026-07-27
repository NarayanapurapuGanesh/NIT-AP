namespace FacultyIQ.Domain.Entities.Recruitment;

public record EvaluationScores
{
    public decimal? ResumeScore { get; init; }
    public decimal? VideoAnalysisScore { get; init; }
    public decimal? CodingTestScore { get; init; }
    public decimal? InteractionScore { get; init; }
    public decimal? FinalAggregateScore { get; init; }

    public static EvaluationScores Empty => new();

    public EvaluationScores WithResumeScore(decimal score) => this with { ResumeScore = score };
    public EvaluationScores WithVideoScore(decimal score) => this with { VideoAnalysisScore = score };
    public EvaluationScores WithCodingScore(decimal score) => this with { CodingTestScore = score };
    public EvaluationScores WithInteractionScore(decimal score) => this with { InteractionScore = score };
    
    public EvaluationScores CalculateFinalScore()
    {
        // Simple equal weighting for now. Can be updated to institutional weights later.
        if (ResumeScore.HasValue && VideoAnalysisScore.HasValue && 
            CodingTestScore.HasValue && InteractionScore.HasValue)
        {
            var average = (ResumeScore.Value + VideoAnalysisScore.Value + 
                           CodingTestScore.Value + InteractionScore.Value) / 4m;
            return this with { FinalAggregateScore = average };
        }
        
        return this;
    }
}
