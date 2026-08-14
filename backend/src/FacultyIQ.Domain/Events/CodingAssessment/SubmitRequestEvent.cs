using System;

namespace FacultyIQ.Domain.Events.CodingAssessment;

public record SubmitRequestEvent(
    Guid SubmissionId,
    Guid QuestionId,
    string Code,
    string Language,
    DateTime Timestamp
);
