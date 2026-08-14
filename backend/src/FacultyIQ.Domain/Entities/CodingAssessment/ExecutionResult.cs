using System;

namespace FacultyIQ.Domain.Entities.CodingAssessment;

public enum ExecutionStatus
{
    ACCEPTED,
    WRONG_ANSWER,
    TIME_LIMIT_EXCEEDED,
    MEMORY_LIMIT_EXCEEDED,
    COMPILE_ERROR,
    RUNTIME_ERROR
}

public class ExecutionResult : Entity
{
    public Guid SubmissionId { get; private set; }
    public ExecutionStatus Status { get; private set; }
    public decimal Score { get; private set; }
    public int ExecutionTimeMs { get; private set; }
    public int MemoryUsageKb { get; private set; }
    public string ConsoleOutput { get; private set; }
    public string ErrorDetails { get; private set; }

    private ExecutionResult(Guid id, Guid submissionId, ExecutionStatus status, decimal score, int executionTimeMs, int memoryUsageKb, string consoleOutput, string errorDetails)
        : base(id)
    {
        SubmissionId = submissionId;
        Status = status;
        Score = score;
        ExecutionTimeMs = executionTimeMs;
        MemoryUsageKb = memoryUsageKb;
        ConsoleOutput = consoleOutput;
        ErrorDetails = errorDetails;
    }

    public static ExecutionResult Create(Guid submissionId, ExecutionStatus status, decimal score, int executionTimeMs, int memoryUsageKb, string consoleOutput, string errorDetails)
    {
        return new ExecutionResult(Guid.NewGuid(), submissionId, status, score, executionTimeMs, memoryUsageKb, consoleOutput, errorDetails);
    }
}
