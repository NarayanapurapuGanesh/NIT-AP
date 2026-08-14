using System;

namespace FacultyIQ.Domain.Events.CodingAssessment;

public record ExecutionCompletedEvent(
    Guid SubmissionId,
    string Status, // ACCEPTED | WRONG_ANSWER | COMPILE_ERROR | TLE | MLE
    int ExecutionTimeMs,
    int MemoryUsageKb,
    int PassedHiddenTests,
    int TotalHiddenTests
);
