using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using FacultyIQ.Application.Abstractions.Messaging;
using FacultyIQ.Domain.Events.CodingAssessment;
using FacultyIQ.Application.Abstractions.Data;

namespace FacultyIQ.Api.Controllers.v1;

[ApiController]
[Route("api/v1/[controller]")]
public class SubmissionsController : ControllerBase
{
    private readonly IEventBus _eventBus;
    private readonly IApplicationDbContext _context;

    public SubmissionsController(IEventBus eventBus, IApplicationDbContext context)
    {
        _eventBus = eventBus;
        _context = context;
    }

    public record RunRequestDto(Guid QuestionId, string Code, string Language);
    public record SubmitRequestDto(Guid QuestionId, string Code, string Language);

    [HttpPost("run")]
    public async Task<IActionResult> Run([FromBody] RunRequestDto request, CancellationToken cancellationToken)
    {
        // For 'Run', we might still use the EventBus or a fast RPC.
        // We'll mimic the asynchronous dispatch for now.
        var runId = Guid.NewGuid();
        
        // In a real system, we'd dispatch a RunEvent instead of Submit
        // We'll use a mocked SubmitRequestEvent for this scaffold.
        var runEvent = new SubmitRequestEvent(runId, request.QuestionId, request.Code, request.Language, DateTime.UtcNow);
        await _eventBus.PublishAsync(runEvent, cancellationToken);
        
        return Accepted(new { runId });
    }

    [HttpPost("submit")]
    public async Task<IActionResult> Submit([FromBody] SubmitRequestDto request, CancellationToken cancellationToken)
    {
        var submissionId = Guid.NewGuid();
        
        // In a real scenario, we'd also persist the Submission to _context before publishing.
        // For Phase 1 scaffold, we dispatch the event for RabbitMQ to pick up.
        var submitEvent = new SubmitRequestEvent(submissionId, request.QuestionId, request.Code, request.Language, DateTime.UtcNow);
        
        await _eventBus.PublishAsync(submitEvent, cancellationToken);
        
        return Accepted(new { submissionId });
    }
}
