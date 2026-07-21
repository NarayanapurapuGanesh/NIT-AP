using Microsoft.Extensions.Diagnostics.HealthChecks;
using FacultyIQ.Application.Abstractions.Vector;

namespace FacultyIQ.Infrastructure.Vector;

public class QdrantHealthCheck : IHealthCheck
{
    private readonly ICollectionManager _collectionManager;

    public QdrantHealthCheck(ICollectionManager collectionManager)
    {
        _collectionManager = collectionManager;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
    {
        try
        {
            await _collectionManager.EnsureCollectionExistsAsync("facultyiq-candidates-v1", 1536, cancellationToken);
            return HealthCheckResult.Healthy("Qdrant vector engine is operational.");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("Qdrant vector engine health check failed.", ex);
        }
    }
}
