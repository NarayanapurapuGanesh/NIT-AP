using Microsoft.Extensions.Diagnostics.HealthChecks;
using FacultyIQ.Application.Abstractions.Storage;

namespace FacultyIQ.Infrastructure.Storage;

public class MinioHealthCheck : IHealthCheck
{
    private readonly IBucketManager _bucketManager;

    public MinioHealthCheck(IBucketManager bucketManager)
    {
        _bucketManager = bucketManager;
    }

    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
    {
        try
        {
            await _bucketManager.EnsureBucketsExistAsync(new[] { "facultyiq-temp" }, cancellationToken);
            return HealthCheckResult.Healthy("MinIO S3 Object Store is operational.");
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("MinIO storage health check failed.", ex);
        }
    }
}
