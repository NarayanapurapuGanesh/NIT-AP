using System;
using FacultyIQ.Domain.Abstractions;

namespace FacultyIQ.Domain.Entities.Recruitment;

public class CandidateApplication : AggregateRoot
{
    public Guid CandidateId { get; private set; }
    public Guid JobRequisitionId { get; private set; }
    public ApplicationStatus Status { get; private set; }
    
    public EvaluationScores Scores { get; private set; } = EvaluationScores.Empty;
    
    public string? ResumeFileUrl { get; private set; }
    public string? VideoFileUrl { get; private set; }
    public string? FinalReport { get; private set; }

    private CandidateApplication() { } // For EF Core

    public static CandidateApplication Create(Guid candidateId, Guid jobRequisitionId)
    {
        return new CandidateApplication
        {
            Id = Guid.NewGuid(),
            CandidateId = candidateId,
            JobRequisitionId = jobRequisitionId,
            Status = ApplicationStatus.Submitted
        };
    }

    public void StartResumeValidation(string resumeUrl)
    {
        if (Status != ApplicationStatus.Submitted)
            throw new InvalidOperationException("Invalid state transition to Resume Validation.");

        ResumeFileUrl = resumeUrl;
        Status = ApplicationStatus.ResumeValidationPending;
    }

    public void CompleteResumeValidation(decimal score)
    {
        if (Status != ApplicationStatus.ResumeValidationPending)
            throw new InvalidOperationException("Application is not in ResumeValidationPending state.");

        Scores = Scores.WithResumeScore(score);
        Status = ApplicationStatus.ResumeValidationCompleted;
    }

    public void StartVideoAnalysis(string videoUrl)
    {
        if (Status != ApplicationStatus.ResumeValidationCompleted)
            throw new InvalidOperationException("Invalid state transition to Video Analysis.");

        VideoFileUrl = videoUrl;
        Status = ApplicationStatus.VideoAnalysisPending;
    }

    public void CompleteVideoAnalysis(decimal score)
    {
        if (Status != ApplicationStatus.VideoAnalysisPending)
            throw new InvalidOperationException("Application is not in VideoAnalysisPending state.");

        Scores = Scores.WithVideoScore(score);
        Status = ApplicationStatus.VideoAnalysisCompleted;
    }

    public void StartCodingTest()
    {
        if (Status != ApplicationStatus.VideoAnalysisCompleted)
            throw new InvalidOperationException("Invalid state transition to Coding Test.");

        Status = ApplicationStatus.CodingTestPending;
    }

    public void CompleteCodingTest(decimal score)
    {
        if (Status != ApplicationStatus.CodingTestPending)
            throw new InvalidOperationException("Application is not in CodingTestPending state.");

        Scores = Scores.WithCodingScore(score);
        Status = ApplicationStatus.CodingTestCompleted;
    }

    public void StartInteractionSession()
    {
        if (Status != ApplicationStatus.CodingTestCompleted)
            throw new InvalidOperationException("Invalid state transition to Interaction Session.");

        Status = ApplicationStatus.InteractionPending;
    }

    public void CompleteInteractionSession(decimal score)
    {
        if (Status != ApplicationStatus.InteractionPending)
            throw new InvalidOperationException("Application is not in InteractionPending state.");

        Scores = Scores.WithInteractionScore(score);
        Status = ApplicationStatus.InteractionCompleted;
    }

    public void GenerateFinalReport(string reportContent, bool isAccepted)
    {
        if (Status != ApplicationStatus.InteractionCompleted)
            throw new InvalidOperationException("Cannot generate final report until all phases are complete.");

        Scores = Scores.CalculateFinalScore();
        FinalReport = reportContent;
        Status = isAccepted ? ApplicationStatus.Accepted : ApplicationStatus.Rejected;
        
        // TODO: Could raise a Domain Event here like ApplicationCompletedDomainEvent
    }
}
