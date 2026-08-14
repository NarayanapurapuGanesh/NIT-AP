using System;

namespace FacultyIQ.Domain.Entities.CodingAssessment;

public enum SubmissionStatus
{
    PENDING,
    RUNNING,
    COMPLETED,
    FAILED
}

public class Submission : Entity
{
    public Guid CandidateId { get; private set; }
    public Guid QuestionId { get; private set; }
    public string Code { get; private set; }
    public string Language { get; private set; }
    public SubmissionStatus Status { get; private set; }
    public DateTime CreatedAt { get; private set; }

    public ExecutionResult ExecutionResult { get; private set; }
    public AiEvaluation AiEvaluation { get; private set; }

    private Submission(Guid id, Guid candidateId, Guid questionId, string code, string language)
        : base(id)
    {
        CandidateId = candidateId;
        QuestionId = questionId;
        Code = code;
        Language = language;
        Status = SubmissionStatus.PENDING;
        CreatedAt = DateTime.UtcNow;
    }

    public static Submission Create(Guid candidateId, Guid questionId, string code, string language)
    {
        return new Submission(Guid.NewGuid(), candidateId, questionId, code, language);
    }

    public void UpdateStatus(SubmissionStatus status)
    {
        Status = status;
    }

    public void AttachExecutionResult(ExecutionResult result)
    {
        ExecutionResult = result;
    }

    public void AttachAiEvaluation(AiEvaluation evaluation)
    {
        AiEvaluation = evaluation;
    }
}
