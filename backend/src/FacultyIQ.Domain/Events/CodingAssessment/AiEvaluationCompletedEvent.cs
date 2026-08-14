using System;
using System.Collections.Generic;

namespace FacultyIQ.Domain.Events.CodingAssessment;

public record AiEvaluationCompletedEvent(
    Guid SubmissionId,
    decimal TeachingQualityScore,
    decimal InterviewReadinessScore,
    string OptimizationSuggestions,
    List<string> FollowUpQuestions
);
