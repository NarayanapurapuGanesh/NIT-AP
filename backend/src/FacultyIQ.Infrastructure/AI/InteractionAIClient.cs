using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using FacultyIQ.Application.Abstractions.Interaction;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Infrastructure.AI;

/// <summary>
/// HTTP client that communicates with the Python Interaction Agent service.
/// Handles serialization, retry logic, and timeout management.
/// </summary>
public class InteractionAIClient : IInteractionAIClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<InteractionAIClient> _logger;
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        PropertyNameCaseInsensitive = true
    };

    public InteractionAIClient(
        HttpClient httpClient,
        ILogger<InteractionAIClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<Result<AIInteractionResponse>> GenerateStudentResponseAsync(
        AIInteractionRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation(
                "[InteractionAI] Processing turn {Turn} for session {Session}",
                request.TurnNumber, request.SessionId);

            var response = await _httpClient.PostAsJsonAsync(
                "/api/interaction/respond", request, JsonOptions, cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                var error = await response.Content.ReadAsStringAsync(cancellationToken);
                _logger.LogError("[InteractionAI] HTTP {Status}: {Error}",
                    response.StatusCode, error);
                return Result.Failure<AIInteractionResponse>(
                    Error.Unexpected("InteractionAI.HttpError",
                        $"AI service returned {response.StatusCode}"));
            }

            var result = await response.Content.ReadFromJsonAsync<AIInteractionResponse>(
                JsonOptions, cancellationToken);

            if (result is null)
            {
                return Result.Failure<AIInteractionResponse>(
                    Error.Unexpected("InteractionAI.NullResponse",
                        "AI service returned null response"));
            }

            return Result.Success(result);
        }
        catch (TaskCanceledException)
        {
            _logger.LogWarning("[InteractionAI] Request timed out for session {Session}",
                request.SessionId);
            return Result.Failure<AIInteractionResponse>(
                Error.Unexpected("InteractionAI.Timeout", "AI service request timed out"));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "[InteractionAI] Unhandled exception for session {Session}",
                request.SessionId);
            return Result.Failure<AIInteractionResponse>(
                Error.Unexpected("InteractionAI.Exception", ex.Message));
        }
    }

    public async Task<Result<InteractionSessionReport>> GenerateFinalEvaluationAsync(
        string sessionId,
        List<ConversationMessage> fullHistory,
        string facultyContextJson,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation("[InteractionAI] Generating final evaluation for session {Session}",
                sessionId);

            var request = new
            {
                session_id = sessionId,
                conversation_history = fullHistory.Select(m => new
                {
                    role = m.Role,
                    content = m.Content,
                    turn_number = m.TurnNumber
                }).ToList(),
                faculty_context_json = facultyContextJson
            };

            var response = await _httpClient.PostAsJsonAsync(
                "/api/interaction/evaluate", request, JsonOptions, cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                var error = await response.Content.ReadAsStringAsync(cancellationToken);
                _logger.LogError("[InteractionAI] Final eval HTTP {Status}: {Error}",
                    response.StatusCode, error);
                return Result.Failure<InteractionSessionReport>(
                    Error.Unexpected("InteractionAI.EvalError",
                        $"Final evaluation failed: {response.StatusCode}"));
            }

            var result = await response.Content.ReadFromJsonAsync<InteractionSessionReport>(
                JsonOptions, cancellationToken);

            return result is not null
                ? Result.Success(result)
                : Result.Failure<InteractionSessionReport>(
                    Error.Unexpected("InteractionAI.NullEvalResponse",
                        "Final evaluation returned null"));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "[InteractionAI] Final evaluation exception for session {Session}",
                sessionId);
            return Result.Failure<InteractionSessionReport>(
                Error.Unexpected("InteractionAI.EvalException", ex.Message));
        }
    }

    public async Task<bool> IsAvailableAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var response = await _httpClient.GetAsync("/api/health", cancellationToken);
            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }
}
