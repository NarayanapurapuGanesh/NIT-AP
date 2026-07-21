using Asp.Versioning;
using Microsoft.AspNetCore.Mvc;

namespace FacultyIQ.Api.Controllers.v1;

[ApiController]
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/[controller]")]
public class HealthController : ControllerBase
{
    [HttpGet]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public IActionResult CheckHealth()
    {
        return Ok(new
        {
            Status = "Healthy",
            Platform = "FacultyIQ Enterprise Engine",
            Environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Production",
            Timestamp = DateTime.UtcNow
        });
    }

    [HttpGet("live")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public IActionResult LivenessCheck()
    {
        return Ok(new { Status = "Live", Timestamp = DateTime.UtcNow });
    }

    [HttpGet("ready")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    public IActionResult ReadinessCheck()
    {
        return Ok(new { Status = "Ready", Timestamp = DateTime.UtcNow });
    }
}
