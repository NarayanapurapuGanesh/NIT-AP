using System;

namespace FacultyIQ.Domain.Events.CodingAssessment;

public record StaticAnalysisCompletedEvent(
    Guid SubmissionId,
    int CyclomaticComplexity,
    decimal MaintainabilityIndex,
    int DuplicateLines
);
