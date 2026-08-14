using System;

namespace FacultyIQ.Domain.Entities.CodingAssessment;

public class StaticAnalysisMetrics : Entity
{
    public Guid SubmissionId { get; private set; }
    public int CyclomaticComplexity { get; private set; }
    public decimal MaintainabilityIndex { get; private set; }
    public int DuplicateLines { get; private set; }
    public string SecurityFlagsJson { get; private set; }

    private StaticAnalysisMetrics(
        Guid id, 
        Guid submissionId, 
        int cyclomaticComplexity, 
        decimal maintainabilityIndex, 
        int duplicateLines, 
        string securityFlagsJson)
        : base(id)
    {
        SubmissionId = submissionId;
        CyclomaticComplexity = cyclomaticComplexity;
        MaintainabilityIndex = maintainabilityIndex;
        DuplicateLines = duplicateLines;
        SecurityFlagsJson = securityFlagsJson;
    }

    public static StaticAnalysisMetrics Create(
        Guid submissionId, 
        int cyclomaticComplexity, 
        decimal maintainabilityIndex, 
        int duplicateLines, 
        string securityFlagsJson)
    {
        return new StaticAnalysisMetrics(
            Guid.NewGuid(), 
            submissionId, 
            cyclomaticComplexity, 
            maintainabilityIndex, 
            duplicateLines, 
            securityFlagsJson);
    }
}
