using System.Threading;
using System.Threading.Tasks;
using FacultyIQ.SharedKernel;
using System;

namespace FacultyIQ.Application.Abstractions.AI;

public record ResumeAnalysisResult(decimal Score, string ExtractedSkills, string RecommendedFeedback);
public record VideoAnalysisResult(decimal CommunicationScore, decimal TechnicalScore, decimal OverallScore, string Transcript, string Feedback);
public record CodeEvaluationResult(decimal LogicScore, decimal SyntaxScore, decimal OverallScore, string CodeFeedback);
public record InteractionEvaluationResult(decimal TeachingScore, decimal KnowledgeScore, decimal OverallScore, string InteractionSummary);

public interface IResumeParserService
{
    Task<Result<ResumeAnalysisResult>> ParseAndEvaluateAsync(string fileUrl, Guid jobRequisitionId, CancellationToken cancellationToken = default);
}

public interface IVideoAnalysisService
{
    Task<Result<VideoAnalysisResult>> AnalyzeDemoVideoAsync(string videoUrl, CancellationToken cancellationToken = default);
}

public interface ICodeEvaluationService
{
    Task<Result<CodeEvaluationResult>> EvaluateCandidateCodeAsync(string sourceCode, string language, string promptId, CancellationToken cancellationToken = default);
}

public interface IInteractionBotService
{
    Task<Result<InteractionEvaluationResult>> EvaluateSessionTranscriptAsync(string transcriptOrSessionId, CancellationToken cancellationToken = default);
}
