namespace FacultyIQ.Application.Abstractions.Storage;

public record FileMetadata(
    string FileName,
    string ContentType,
    long SizeBytes,
    string BucketName,
    DateTime CreatedAtUtc,
    IDictionary<string, string>? CustomMetadata = null
);

public record UploadFileResult(
    string ObjectName,
    string BucketName,
    string ContentType,
    long SizeBytes,
    string? ETag
);

public record StorageFileResponse(
    Stream Stream,
    string ContentType,
    string FileName,
    long SizeBytes
);
