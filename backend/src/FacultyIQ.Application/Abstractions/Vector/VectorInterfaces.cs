using FacultyIQ.SharedKernel;

namespace FacultyIQ.Application.Abstractions.Vector;

public interface IVectorService
{
    Task<Result> UpsertVectorsAsync(
        string collectionName,
        IEnumerable<VectorRecord> records,
        CancellationToken cancellationToken = default);

    Task<Result<IReadOnlyList<SearchResult>>> SearchAsync(
        string collectionName,
        float[] queryVector,
        int limit = 10,
        float minScore = 0.0f,
        CancellationToken cancellationToken = default);

    Task<Result> DeleteVectorAsync(
        string collectionName,
        Guid recordId,
        CancellationToken cancellationToken = default);
}

public interface ICollectionManager
{
    Task EnsureCollectionExistsAsync(string collectionName, uint vectorSize = 1536, CancellationToken cancellationToken = default);
    Task<bool> CollectionExistsAsync(string collectionName, CancellationToken cancellationToken = default);
    Task<Result<CollectionDetails>> GetCollectionDetailsAsync(string collectionName, CancellationToken cancellationToken = default);
}

public interface IEmbeddingGenerator
{
    Task<Result<float[]>> GenerateEmbeddingAsync(string text, CancellationToken cancellationToken = default);
}
