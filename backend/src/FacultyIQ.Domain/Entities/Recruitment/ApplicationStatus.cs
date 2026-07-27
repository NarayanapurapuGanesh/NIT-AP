namespace FacultyIQ.Domain.Entities.Recruitment;

public enum ApplicationStatus
{
    Submitted = 0,
    ResumeValidationPending = 1,
    ResumeValidationCompleted = 2,
    VideoAnalysisPending = 3,
    VideoAnalysisCompleted = 4,
    CodingTestPending = 5,
    CodingTestCompleted = 6,
    InteractionPending = 7,
    InteractionCompleted = 8,
    FinalReview = 9,
    Accepted = 10,
    Rejected = 11
}
