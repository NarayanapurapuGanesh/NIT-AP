using System;
using System.Collections.Generic;

namespace FacultyIQ.Domain.Entities.CodingAssessment;

public class AiEvaluation : Entity
{
    public Guid SubmissionId { get; private set; }
    public string AlgorithmChoiceFeedback { get; private set; }
    public string OptimizationSuggestions { get; private set; }
    public decimal TeachingQualityScore { get; private set; }
    public decimal InterviewReadinessScore { get; private set; }
    public List<string> FollowUpVivaQuestions { get; private set; }
    public DateTime CreatedAt { get; private set; }

    private AiEvaluation(
        Guid id, 
        Guid submissionId, 
        string algorithmChoiceFeedback, 
        string optimizationSuggestions, 
        decimal teachingQualityScore, 
        decimal interviewReadinessScore, 
        List<string> followUpVivaQuestions)
        : base(id)
    {
        SubmissionId = submissionId;
        AlgorithmChoiceFeedback = algorithmChoiceFeedback;
        OptimizationSuggestions = optimizationSuggestions;
        TeachingQualityScore = teachingQualityScore;
        InterviewReadinessScore = interviewReadinessScore;
        FollowUpVivaQuestions = followUpVivaQuestions ?? new List<string>();
        CreatedAt = DateTime.UtcNow;
    }

    public static AiEvaluation Create(
        Guid submissionId, 
        string algorithmChoiceFeedback, 
        string optimizationSuggestions, 
        decimal teachingQualityScore, 
        decimal interviewReadinessScore, 
        List<string> followUpVivaQuestions)
    {
        return new AiEvaluation(
            Guid.NewGuid(), 
            submissionId, 
            algorithmChoiceFeedback, 
            optimizationSuggestions, 
            teachingQualityScore, 
            interviewReadinessScore, 
            followUpVivaQuestions);
    }
}
