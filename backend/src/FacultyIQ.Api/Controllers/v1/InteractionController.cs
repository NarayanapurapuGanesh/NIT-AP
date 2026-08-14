using Asp.Versioning;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using FacultyIQ.Api.Hubs;
using FacultyIQ.Application.Abstractions.Interaction;
using FacultyIQ.Domain.Entities.Interaction;

namespace FacultyIQ.Api.Controllers.v1;

/// <summary>
/// REST API controller for the Interaction Intelligence Agent.
/// Manages teaching interaction sessions between AI students and faculty members.
/// </summary>
[ApiController]
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/interaction")]
public class InteractionController : ControllerBase
{
    private readonly IInteractionSessionService _interactionService;
    private readonly IHubContext<InteractionHub> _hubContext;

    public InteractionController(
        IInteractionSessionService interactionService,
        IHubContext<InteractionHub> hubContext)
    {
        _interactionService = interactionService;
        _hubContext = hubContext;
    }

    /// <summary>
    /// Start a new teaching interaction session.
    /// Creates the session, selects a student persona, and generates the opening AI student message.
    /// </summary>
    [HttpPost("start")]
    [ProducesResponseType(typeof(StartInteractionResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> StartSession(
        [FromBody] StartInteractionRequest request,
        CancellationToken cancellationToken)
    {
        var result = await _interactionService.StartSessionAsync(request, cancellationToken);

        if (result.IsFailure)
            return BadRequest(new { error = result.Error.Description });

        return Ok(result.Value);
    }

    /// <summary>
    /// Faculty sends a message during the interaction.
    /// The AI evaluates teaching quality, generates a student response,
    /// and pushes real-time updates via SignalR.
    /// </summary>
    [HttpPost("message")]
    [ProducesResponseType(typeof(StudentResponseResult), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> SendMessage(
        [FromBody] FacultyMessageRequest request,
        CancellationToken cancellationToken)
    {
        var result = await _interactionService.ProcessFacultyMessageAsync(request, cancellationToken);

        if (result.IsFailure)
        {
            if (result.Error.Code.Contains("NotFound"))
                return NotFound(new { error = result.Error.Description });
            return BadRequest(new { error = result.Error.Description });
        }

        var response = result.Value;

        // Push real-time updates via SignalR
        var groupName = $"interaction-{request.SessionId}";
        await _hubContext.Clients.Group(groupName)
            .SendAsync("ReceiveStudentMessage", new
            {
                message = response.StudentMessage,
                turnNumber = response.TurnNumber,
                bloomLevel = response.CurrentBloomLevel.ToString(),
                sessionComplete = response.SessionComplete
            }, cancellationToken);

        await _hubContext.Clients.Group(groupName)
            .SendAsync("ReceiveAnalyticsUpdate", response.Analytics, cancellationToken);

        return Ok(response);
    }

    /// <summary>
    /// End the interaction session and trigger final comprehensive evaluation.
    /// </summary>
    [HttpPost("end")]
    [ProducesResponseType(typeof(InteractionSessionReport), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> EndSession(
        [FromQuery] Guid sessionId,
        CancellationToken cancellationToken)
    {
        var result = await _interactionService.EndSessionAsync(sessionId, cancellationToken);

        if (result.IsFailure)
        {
            if (result.Error.Code.Contains("NotFound"))
                return NotFound(new { error = result.Error.Description });
            return BadRequest(new { error = result.Error.Description });
        }

        // Notify connected clients that the session has ended
        await _hubContext.Clients.Group($"interaction-{sessionId}")
            .SendAsync("SessionEnded", result.Value, cancellationToken);

        return Ok(result.Value);
    }

    /// <summary>
    /// Trigger evaluation for a completed session.
    /// </summary>
    [HttpPost("evaluate")]
    [ProducesResponseType(typeof(InteractionSessionReport), StatusCodes.Status200OK)]
    public async Task<IActionResult> Evaluate(
        [FromQuery] Guid sessionId,
        CancellationToken cancellationToken)
    {
        var result = await _interactionService.EndSessionAsync(sessionId, cancellationToken);

        if (result.IsFailure)
            return BadRequest(new { error = result.Error.Description });

        return Ok(result.Value);
    }

    /// <summary>
    /// Pause the interaction session, preserving all state.
    /// </summary>
    [HttpPost("{sessionId}/pause")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> PauseSession(
        Guid sessionId,
        CancellationToken cancellationToken)
    {
        var result = await _interactionService.PauseSessionAsync(sessionId, cancellationToken);

        if (result.IsFailure)
            return BadRequest(new { error = result.Error.Description });

        await _hubContext.Clients.Group($"interaction-{sessionId}")
            .SendAsync("SessionPaused", cancellationToken);

        return Ok(new { status = "paused" });
    }

    /// <summary>
    /// Resume a paused interaction session.
    /// </summary>
    [HttpPost("{sessionId}/resume")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public async Task<IActionResult> ResumeSession(
        Guid sessionId,
        CancellationToken cancellationToken)
    {
        var result = await _interactionService.ResumeSessionAsync(sessionId, cancellationToken);

        if (result.IsFailure)
            return BadRequest(new { error = result.Error.Description });

        await _hubContext.Clients.Group($"interaction-{sessionId}")
            .SendAsync("SessionResumed", cancellationToken);

        return Ok(new { status = "active" });
    }

    /// <summary>
    /// Get the full session report with all evidence, scores, and recommendations.
    /// </summary>
    [HttpGet("{sessionId}/report")]
    [ProducesResponseType(typeof(InteractionSessionReport), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetReport(
        Guid sessionId,
        CancellationToken cancellationToken)
    {
        var result = await _interactionService.GetSessionReportAsync(sessionId, cancellationToken);

        if (result.IsFailure)
            return NotFound(new { error = result.Error.Description });

        return Ok(result.Value);
    }

    /// <summary>
    /// Get the evidence timeline for a session.
    /// </summary>
    [HttpGet("{sessionId}/evidence")]
    [ProducesResponseType(typeof(InteractionSessionReport), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetEvidence(
        Guid sessionId,
        CancellationToken cancellationToken)
    {
        var result = await _interactionService.GetSessionReportAsync(sessionId, cancellationToken);

        if (result.IsFailure)
            return NotFound(new { error = result.Error.Description });

        return Ok(new { evidence = result.Value.Evidence });
    }

    /// <summary>
    /// Get live analytics snapshot for the dashboard.
    /// </summary>
    [HttpGet("{sessionId}/analytics")]
    [ProducesResponseType(typeof(InteractionAnalyticsSnapshot), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetAnalytics(
        Guid sessionId,
        CancellationToken cancellationToken)
    {
        var result = await _interactionService.GetSessionAnalyticsAsync(sessionId, cancellationToken);

        if (result.IsFailure)
            return NotFound(new { error = result.Error.Description });

        return Ok(result.Value);
    }
}
