using FacultyIQ.SharedKernel;

namespace FacultyIQ.Application.Abstractions.Storage;

public interface IStorageService
{
    Task<Result<UploadFileResult>> UploadFileAsync(
        string bucketName,
        string objectName,
        Stream contentStream,
        string contentType,
        long sizeBytes,
        IDictionary<string, string>? metadata = null,
        CancellationToken cancellationToken = default);

    Task<Result<StorageFileResponse>> DownloadFileAsync(
        string bucketName,
        string objectName,
        CancellationToken cancellationToken = default);

    Task<Result<string>> GetPresignedUrlAsync(
        string bucketName,
        string objectName,
        int expirySeconds = 3600,
        CancellationToken cancellationToken = default);

    Task<Result> DeleteFileAsync(
        string bucketName,
        string objectName,
        CancellationToken cancellationToken = default);

    Task<Result<FileMetadata>> GetFileMetadataAsync(
        string bucketName,
        string objectName,
        CancellationToken cancellationToken = default);
}

public interface IBucketManager
{
    Task EnsureBucketsExistAsync(IEnumerable<string> bucketNames, CancellationToken cancellationToken = default);
    Task<bool> BucketExistsAsync(string bucketName, CancellationToken cancellationToken = default);
}

public interface IStorageProvider : IStorageService, IBucketManager
{
    string ProviderName { get; }
}
