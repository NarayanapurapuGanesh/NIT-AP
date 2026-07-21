using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using Qdrant.Client;
using Qdrant.Client.Grpc;
using FacultyIQ.Application.Abstractions.Vector;
using FacultyIQ.Application.Options;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Infrastructure.Vector;

public class QdrantVectorService : IVectorService, ICollectionManager
{
    private readonly QdrantClient _client;
    private readonly QdrantOptions _options;
    private readonly ILogger<QdrantVectorService> _logger;

    public QdrantVectorService(
        IOptions<QdrantOptions> options,
        ILogger<QdrantVectorService> logger)
    {
        _options = options.Value;
        _logger = logger;

        var uri = new Uri(_options.Endpoint);
        _client = new QdrantClient(host: uri.Host, port: _options.Endpoint.EndsWith("6334") ? uri.Port : 6334, apiKey: _options.ApiKey);
    }

    public async Task EnsureCollectionExistsAsync(string collectionName, uint vectorSize = 1536, CancellationToken cancellationToken = default)
    {
        var exists = await CollectionExistsAsync(collectionName, cancellationToken);
        if (!exists)
        {
            await _client.CreateCollectionAsync(
                collectionName: collectionName,
                vectorsConfig: new VectorParams { Size = vectorSize, Distance = Distance.Cosine },
                cancellationToken: cancellationToken
            );
            _logger.LogInformation("Qdrant collection '{CollectionName}' created successfully.", collectionName);
        }
    }

    public async Task<bool> CollectionExistsAsync(string collectionName, CancellationToken cancellationToken = default)
    {
        try
        {
            return await _client.CollectionExistsAsync(collectionName, cancellationToken);
        }
        catch
        {
            return false;
        }
    }

    public async Task<Result<CollectionDetails>> GetCollectionDetailsAsync(string collectionName, CancellationToken cancellationToken = default)
    {
        try
        {
            var info = await _client.GetCollectionInfoAsync(collectionName, cancellationToken);
            return Result.Success(new CollectionDetails(
                collectionName,
                info.IndexedVectorsCount,
                info.PointsCount,
                (uint)info.Config.Params.VectorsConfig.Params.Size,
                info.Config.Params.VectorsConfig.Params.Distance.ToString()
            ));
        }
        catch (Exception ex)
        {
            return Result.Failure<CollectionDetails>(Error.NotFound("Qdrant.CollectionNotFound", ex.Message));
        }
    }

    public async Task<Result> UpsertVectorsAsync(
        string collectionName,
        IEnumerable<VectorRecord> records,
        CancellationToken cancellationToken = default)
    {
        try
        {
            await EnsureCollectionExistsAsync(collectionName, cancellationToken: cancellationToken);

            var points = records.Select(r =>
            {
                var point = new PointStruct
                {
                    Id = new PointId { Num = (ulong)Math.Abs(r.Id.GetHashCode()) },
                    Vectors = r.Vector
                };

                foreach (var (key, value) in r.Payload)
                {
                    point.Payload.Add(key, value?.ToString() ?? string.Empty);
                }

                return point;
            }).ToList();

            await _client.UpsertAsync(collectionName, points, cancellationToken: cancellationToken);
            return Result.Success();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to upsert vectors into Qdrant collection {CollectionName}", collectionName);
            return Result.Failure(Error.Unexpected("Qdrant.UpsertFailed", ex.Message));
        }
    }

    public async Task<Result<IReadOnlyList<SearchResult>>> SearchAsync(
        string collectionName,
        float[] queryVector,
        int limit = 10,
        float minScore = 0.0f,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var searchPoints = await _client.SearchAsync(
                collectionName: collectionName,
                vector: queryVector,
                limit: (ulong)limit,
                scoreThreshold: minScore,
                cancellationToken: cancellationToken
            );

            var results = searchPoints.Select(p => new SearchResult(
                Guid.NewGuid(),
                p.Score,
                p.Payload.ToDictionary(kvp => kvp.Key, kvp => (object)kvp.Value.StringValue)
            )).ToList();

            return Result.Success<IReadOnlyList<SearchResult>>(results);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to search vectors in Qdrant collection {CollectionName}", collectionName);
            return Result.Failure<IReadOnlyList<SearchResult>>(Error.Unexpected("Qdrant.SearchFailed", ex.Message));
        }
    }

    public async Task<Result> DeleteVectorAsync(
        string collectionName,
        Guid recordId,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var pointId = (ulong)Math.Abs(recordId.GetHashCode());
            await _client.DeleteAsync(collectionName, pointId, cancellationToken: cancellationToken);
            return Result.Success();
        }
        catch (Exception ex)
        {
            return Result.Failure(Error.Unexpected("Qdrant.DeleteFailed", ex.Message));
        }
    }
}
