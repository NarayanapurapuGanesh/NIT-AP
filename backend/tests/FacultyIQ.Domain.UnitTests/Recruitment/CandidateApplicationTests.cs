using System;
using FacultyIQ.Domain.Entities.Recruitment;
using Xunit;

namespace FacultyIQ.Domain.UnitTests.Recruitment;

public class CandidateApplicationTests
{
    [Fact]
    public void Create_Should_InitializeApplicationInSubmittedState()
    {
        // Arrange
        var candidateId = Guid.NewGuid();
        var jobId = Guid.NewGuid();

        // Act
        var application = CandidateApplication.Create(candidateId, jobId);

        // Assert
        Assert.Equal(candidateId, application.CandidateId);
        Assert.Equal(jobId, application.JobRequisitionId);
        Assert.Equal(ApplicationStatus.Submitted, application.Status);
        Assert.NotNull(application.Scores);
    }

    [Fact]
    public void ValidTransitions_Should_ProgressCorrectlyThroughAllPhases()
    {
        // Arrange
        var application = CandidateApplication.Create(Guid.NewGuid(), Guid.NewGuid());

        // Phase 1: Resume Validation
        application.StartResumeValidation("resume.pdf");
        Assert.Equal(ApplicationStatus.ResumeValidationPending, application.Status);
        application.CompleteResumeValidation(85m);
        Assert.Equal(ApplicationStatus.ResumeValidationCompleted, application.Status);
        Assert.Equal(85m, application.Scores.ResumeScore);

        // Phase 2: Video Analysis
        application.StartVideoAnalysis("video.mp4");
        Assert.Equal(ApplicationStatus.VideoAnalysisPending, application.Status);
        application.CompleteVideoAnalysis(90m);
        Assert.Equal(ApplicationStatus.VideoAnalysisCompleted, application.Status);
        Assert.Equal(90m, application.Scores.VideoAnalysisScore);

        // Phase 3: Coding Test
        application.StartCodingTest();
        Assert.Equal(ApplicationStatus.CodingTestPending, application.Status);
        application.CompleteCodingTest(95m);
        Assert.Equal(ApplicationStatus.CodingTestCompleted, application.Status);
        Assert.Equal(95m, application.Scores.CodingTestScore);

        // Phase 4: Interaction Session
        application.StartInteractionSession();
        Assert.Equal(ApplicationStatus.InteractionPending, application.Status);
        application.CompleteInteractionSession(88m);
        Assert.Equal(ApplicationStatus.InteractionCompleted, application.Status);
        Assert.Equal(88m, application.Scores.InteractionScore);

        // Final Report
        application.GenerateFinalReport("Candidate looks good.", true);
        Assert.Equal(ApplicationStatus.Accepted, application.Status);
        
        // (85 + 90 + 95 + 88) / 4 = 89.5
        Assert.Equal(89.5m, application.Scores.FinalAggregateScore);
        Assert.Equal("Candidate looks good.", application.FinalReport);
    }

    [Fact]
    public void InvalidTransition_Should_ThrowException()
    {
        // Arrange
        var application = CandidateApplication.Create(Guid.NewGuid(), Guid.NewGuid());

        // Act & Assert
        // Trying to skip straight to Coding Test without doing resume/video first
        var ex = Assert.Throws<InvalidOperationException>(() => application.StartCodingTest());
        Assert.Equal("Invalid state transition to Coding Test.", ex.Message);
    }
}
