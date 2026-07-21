using FacultyIQ.SharedKernel;

namespace FacultyIQ.Application.Abstractions.AI;

public interface IAIService
{
    Task<Result<AICompletionResponse>> GenerateCompletionAsync(
        AICompletionRequest request,
        CancellationToken cancellationToken = default);
}

public interface IOllamaClient : IAIService
{
    Task<Result<IReadOnlyList<ModelMetadata>>> GetAvailableModelsAsync(CancellationToken cancellationToken = default);
    Task<bool> IsModelAvailableAsync(string modelName, CancellationToken cancellationToken = default);
}

public interface IModelRegistry
{
    Task<IReadOnlyList<ModelMetadata>> GetRegisteredModelsAsync(CancellationToken cancellationToken = default);
    Task<bool> ValidateModelReadinessAsync(string modelName, CancellationToken cancellationToken = default);
}

public interface IPromptRegistry
{
    Task<Result<PromptTemplate>> GetPromptTemplateAsync(string promptId, string? version = null, CancellationToken cancellationToken = default);
    Task<string> RenderPromptAsync(string promptId, IDictionary<string, string> variables, CancellationToken cancellationToken = default);
}

public interface IAIProvider : IAIService
{
    string ProviderName { get; }
    bool IsSupported(string modelName);
}
