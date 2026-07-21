using FacultyIQ.Application.Abstractions.AI;

namespace FacultyIQ.Infrastructure.AI;

public class ModelRegistry : IModelRegistry
{
    private readonly IOllamaClient _ollamaClient;

    public ModelRegistry(IOllamaClient ollamaClient)
    {
        _ollamaClient = ollamaClient;
    }

    public async Task<IReadOnlyList<ModelMetadata>> GetRegisteredModelsAsync(CancellationToken cancellationToken = default)
    {
        var result = await _ollamaClient.GetAvailableModelsAsync(cancellationToken);
        if (result.IsSuccess)
        {
            return result.Value;
        }

        return new List<ModelMetadata>
        {
            new("llama3:8b", "Ollama", 4700000000, "8B", false)
        };
    }

    public async Task<bool> ValidateModelReadinessAsync(string modelName, CancellationToken cancellationToken = default)
    {
        return await _ollamaClient.IsModelAvailableAsync(modelName, cancellationToken);
    }
}
