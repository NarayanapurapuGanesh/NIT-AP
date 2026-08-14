using FacultyIQ.SharedKernel;

namespace FacultyIQ.Application.Abstractions.Interaction;

/// <summary>
/// Core service interface for managing teaching interaction sessions.
/// Orchestrates the interaction between the AI student simulator and the faculty member.
/// </summary>
public interface IInteractionSessionService
{
    /// <summary>
    /// Creates and starts a new interaction session with the selected student persona.
    /// Returns the opening AI student message.
    /// </summary>
    Task<Result<StartInteractionResponse>> StartSessionAsync(
        StartInteractionRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Processes a faculty message: evaluates teaching quality, generates AI student response,
    /// updates Bloom level, and returns real-time analytics.
    /// </summary>
    Task<Result<StudentResponseResult>> ProcessFacultyMessageAsync(
        FacultyMessageRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Pauses the interaction session, preserving state.
    /// </summary>
    Task<Result> PauseSessionAsync(Guid sessionId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Resumes a paused interaction session.
    /// </summary>
    Task<Result> ResumeSessionAsync(Guid sessionId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Ends the interaction session and triggers final evaluation.
    /// </summary>
    Task<Result<InteractionSessionReport>> EndSessionAsync(
        Guid sessionId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets the full session report with all evidence, scores, and recommendations.
    /// </summary>
    Task<Result<InteractionSessionReport>> GetSessionReportAsync(
        Guid sessionId,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets real-time analytics snapshot for the dashboard.
    /// </summary>
    Task<Result<InteractionAnalyticsSnapshot>> GetSessionAnalyticsAsync(
        Guid sessionId,
        CancellationToken cancellationToken = default);
}

/// <summary>
/// Interface for the AI-powered teaching quality analysis pipeline.
/// Communicates with the Python interaction-agent service.
/// </summary>
public interface IInteractionAIClient
{
    /// <summary>
    /// Sends the current interaction state to the AI service and receives the student response
    /// plus teaching evaluation metrics.
    /// </summary>
    Task<Result<AIInteractionResponse>> GenerateStudentResponseAsync(
        AIInteractionRequest request,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Requests a final comprehensive evaluation of the entire session.
    /// </summary>
    Task<Result<InteractionSessionReport>> GenerateFinalEvaluationAsync(
        string sessionId,
        List<ConversationMessage> fullHistory,
        string facultyContextJson,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Health check for the AI service.
    /// </summary>
    Task<bool> IsAvailableAsync(CancellationToken cancellationToken = default);
}
