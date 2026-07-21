using Microsoft.Extensions.Diagnostics.HealthChecks;
using FacultyIQ.Application.Abstractions.AI;

namespace FacultyIQ.Infrastructure.AI;

public class OllamaHealthCheck : IHealthCheck
{
    private readonly IOllamaClient _ollamaClient;

    public OllamaHealthCheck(IOllamaClient ollamaClient)
    {
        _ollamaClient = ollamaClient;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
    {
        try
        {
            var result = await _ollamaClient.GetAvailableModelsAsync(cancellationToken);
            if (result.IsSuccess)
            {
                return HealthCheckResult.Healthy($"Ollama local AI engine is online. Discovered {result.Value.Count} models.");
            }

            return HealthCheckResult.Degraded($"Ollama reachable but returned error: {result.Error.Description}");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Ollama local AI engine connection failed.", ex);
        }
    }
}
