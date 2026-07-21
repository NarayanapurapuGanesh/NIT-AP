namespace FacultyIQ.Application.Options;

public class DatabaseOptions
{
    public const string SectionName = "Database";
    public string ConnectionString { get; set; } = string.Empty;
    public int MaxRetryCount { get; set; } = 5;
    public int CommandTimeout { get; set; } = 30;
    public bool EnableSensitiveDataLogging { get; set; } = false;
    public bool EnableDetailedErrors { get; set; } = false;
}

public class RedisOptions
{
    public const string SectionName = "Redis";
    public string ConnectionString { get; set; } = string.Empty;
    public int DefaultExpirationMinutes { get; set; } = 60;
}

public class QdrantOptions
{
    public const string SectionName = "Qdrant";
    public string Endpoint { get; set; } = "http://localhost:6333";
    public string? ApiKey { get; set; }
}

public class MinioOptions
{
    public const string SectionName = "Minio";
    public string Endpoint { get; set; } = "http://localhost:9000";
    public string AccessKey { get; set; } = string.Empty;
    public string SecretKey { get; set; } = string.Empty;
    public string BucketName { get; set; } = "facultyiq-dossiers";
}

public class OllamaOptions
{
    public const string SectionName = "Ollama";
    public string Endpoint { get; set; } = "http://localhost:11434";
    public string DefaultModel { get; set; } = "llama3:8b";
}
