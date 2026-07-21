using Microsoft.Extensions.Options;
using Minio;
using Minio.DataModel.Args;
using FacultyIQ.Application.Abstractions.Storage;
using FacultyIQ.Application.Options;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Infrastructure.Storage;

public class MinioStorageService : IStorageProvider
{
    private readonly IMinioClient _minioClient;
    private readonly MinioOptions _options;

    public MinioStorageService(IOptions<MinioOptions> options)
    {
        _options = options.Value;
        
        var uri = new Uri(_options.Endpoint);
        var endpoint = uri.Authority;
        var secure = uri.Scheme.Equals("https", StringComparison.OrdinalIgnoreCase);

        _minioClient = new MinioClient()
            .WithEndpoint(endpoint)
            .WithCredentials(_options.AccessKey, _options.SecretKey)
            .WithSSL(secure)
            .Build();
    }

    public string ProviderName => "MinIO S3 Provider";

    public async Task EnsureBucketsExistAsync(IEnumerable<string> bucketNames, CancellationToken cancellationToken = default)
    {
        foreach (var bucketName in bucketNames)
        {
            var exists = await BucketExistsAsync(bucketName, cancellationToken);
            if (!exists)
            {
                var makeArgs = new MakeBucketArgs().WithBucket(bucketName);
                await _minioClient.MakeBucketAsync(makeArgs, cancellationToken);
            }
        }
    }

    public async Task<bool> BucketExistsAsync(string bucketName, CancellationToken cancellationToken = default)
    {
        var existsArgs = new BucketExistsArgs().WithBucket(bucketName);
        return await _minioClient.BucketExistsAsync(existsArgs, cancellationToken);
    }

    public async Task<Result<UploadFileResult>> UploadFileAsync(
        string bucketName,
        string objectName,
        Stream contentStream,
        string contentType,
        long sizeBytes,
        IDictionary<string, string>? metadata = null,
        CancellationToken cancellationToken = default)
    {
        try
        {
            await EnsureBucketsExistAsync(new[] { bucketName }, cancellationToken);

            var putObjectArgs = new PutObjectArgs()
                .WithBucket(bucketName)
                .WithObject(objectName)
                .WithStreamData(contentStream)
                .WithObjectSize(sizeBytes)
                .WithContentType(contentType);

            if (metadata is not null)
            {
                putObjectArgs.WithHeaders(metadata);
            }

            var response = await _minioClient.PutObjectAsync(putObjectArgs, cancellationToken);
            return Result.Success(new UploadFileResult(objectName, bucketName, contentType, sizeBytes, response.Etag));
        }
        catch (Exception ex)
        {
            return Result.Failure<UploadFileResult>(Error.Unexpected("Storage.UploadFailed", ex.Message));
        }
    }

    public async Task<Result<StorageFileResponse>> DownloadFileAsync(
        string bucketName,
        string objectName,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var memoryStream = new MemoryStream();
            var statArgs = new StatObjectArgs().WithBucket(bucketName).WithObject(objectName);
            var stat = await _minioClient.StatObjectAsync(statArgs, cancellationToken);

            var getObjectArgs = new GetObjectArgs()
                .WithBucket(bucketName)
                .WithObject(objectName)
                .WithCallbackStream(stream => stream.CopyTo(memoryStream));

            await _minioClient.GetObjectAsync(getObjectArgs, cancellationToken);
            memoryStream.Position = 0;

            return Result.Success(new StorageFileResponse(memoryStream, stat.ContentType, objectName, stat.Size));
        }
        catch (Exception ex)
        {
            return Result.Failure<StorageFileResponse>(Error.NotFound("Storage.FileNotFound", ex.Message));
        }
    }

    public async Task<Result<string>> GetPresignedUrlAsync(
        string bucketName,
        string objectName,
        int expirySeconds = 3600,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var presignedArgs = new PresignedGetObjectArgs()
                .WithBucket(bucketName)
                .WithObject(objectName)
                .WithExpiry(expirySeconds);

            var url = await _minioClient.PresignedGetObjectAsync(presignedArgs);
            return Result.Success(url);
        }
        catch (Exception ex)
        {
            return Result.Failure<string>(Error.Unexpected("Storage.PresignedUrlFailed", ex.Message));
        }
    }

    public async Task<Result> DeleteFileAsync(
        string bucketName,
        string objectName,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var removeArgs = new RemoveObjectArgs().WithBucket(bucketName).WithObject(objectName);
            await _minioClient.RemoveObjectAsync(removeArgs, cancellationToken);
            return Result.Success();
        }
        catch (Exception ex)
        {
            return Result.Failure(Error.Unexpected("Storage.DeleteFailed", ex.Message));
        }
    }

    public async Task<Result<FileMetadata>> GetFileMetadataAsync(
        string bucketName,
        string objectName,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var statArgs = new StatObjectArgs().WithBucket(bucketName).WithObject(objectName);
            var stat = await _minioClient.StatObjectAsync(statArgs, cancellationToken);

            return Result.Success(new FileMetadata(
                objectName,
                stat.ContentType,
                stat.Size,
                bucketName,
                stat.LastModified
            ));
        }
        catch (Exception ex)
        {
            return Result.Failure<FileMetadata>(Error.NotFound("Storage.MetadataNotFound", ex.Message));
        }
    }
}
