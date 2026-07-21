using System.Diagnostics;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using FacultyIQ.Application.Abstractions.AI;
using FacultyIQ.Application.Options;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Infrastructure.AI;

public class OllamaClient : IOllamaClient, IAIProvider
{
    private readonly HttpClient _httpClient;
    private readonly OllamaOptions _options;
    private readonly ILogger<OllamaClient> _logger;

    public OllamaClient(
        HttpClient httpClient,
        IOptions<OllamaOptions> options,
        ILogger<OllamaClient> logger)
    {
        _httpClient = httpClient;
        _options = options.Value;
        _logger = logger;

        _httpClient.BaseAddress = new Uri(_options.Endpoint);
    }

    public string ProviderName => "Ollama Local AI Provider";

    public bool IsSupported(string modelName) => true;

    public async Task<Result<AICompletionResponse>> GenerateCompletionAsync(
        AICompletionRequest request,
        CancellationToken cancellationToken = default)
    {
        var modelToUse = request.Model ?? _options.DefaultModel;
        var stopwatch = Stopwatch.StartNew();

        try
        {
            var payload = new
            {
                model = modelToUse,
                prompt = $"{request.SystemPrompt}\n\n{request.UserPrompt}",
                stream = false,
                options = new
                {
                    temperature = request.Temperature,
                    num_predict = request.MaxTokens
                }
            };

            var httpResponse = await _httpClient.PostAsJsonAsync("/api/generate", payload, cancellationToken);
            stopwatch.Stop();

            if (!httpResponse.IsSuccessStatusCode)
            {
                var errBody = await httpResponse.Content.ReadAsStringAsync(cancellationToken);
                _logger.LogError("Ollama generation failed with status {StatusCode}: {Error}", httpResponse.StatusCode, errBody);
                return Result.Failure<AICompletionResponse>(Error.Unexpected("Ollama.HttpError", $"Ollama request failed: {httpResponse.StatusCode}"));
            }

            var resultObj = await httpResponse.Content.ReadFromJsonAsync<OllamaGenerateResponse>(cancellationToken: cancellationToken);
            if (resultObj is null)
            {
                return Result.Failure<AICompletionResponse>(Error.Unexpected("Ollama.NullResponse", "Ollama returned null response payload."));
            }

            return Result.Success(new AICompletionResponse(
                resultObj.Response,
                modelToUse,
                resultObj.PromptEvalCount ?? 0,
                resultObj.EvalCount ?? 0,
                stopwatch.ElapsedMilliseconds,
                true
            ));
        }
        catch (Exception ex)
        {
            stopwatch.Stop();
            _logger.LogError(ex, "Unhandled exception calling Ollama inference endpoint.");
            return Result.Failure<AICompletionResponse>(Error.Unexpected("Ollama.Exception", ex.Message));
        }
    }

    public async Task<Result<IReadOnlyList<ModelMetadata>>> GetAvailableModelsAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            var response = await _httpClient.GetFromJsonAsync<OllamaTagsResponse>("/api/tags", cancellationToken);
            if (response is null)
            {
                return Result.Success<IReadOnlyList<ModelMetadata>>(Array.Empty<ModelMetadata>());
            }

            var models = response.Models.Select(m => new ModelMetadata(
                m.Name,
                "Ollama",
                m.Size,
                m.Details?.ParameterSize ?? "Unknown",
                true
            )).ToList();

            return Result.Success<IReadOnlyList<ModelMetadata>>(models);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to query Ollama model tags endpoint.");
            return Result.Failure<IReadOnlyList<ModelMetadata>>(Error.Unexpected("Ollama.TagsFailed", ex.Message));
        }
    }

    public async Task<bool> IsModelAvailableAsync(string modelName, CancellationToken cancellationToken = default)
    {
        var modelsResult = await GetAvailableModelsAsync(cancellationToken);
        if (modelsResult.IsFailure) return false;

        return modelsResult.Value.Any(m => m.Name.Equals(modelName, StringComparison.OrdinalIgnoreCase));
    }

    private class OllamaGenerateResponse
    {
        [JsonPropertyName("response")]
        public string Response { get; set; } = string.Empty;

        [JsonPropertyName("prompt_eval_count")]
        public int? PromptEvalCount { get; set; }

        [JsonPropertyName("eval_count")]
        public int? EvalCount { get; set; }
    }

    private class OllamaTagsResponse
    {
        [JsonPropertyName("models")]
        public List<OllamaModelItem> Models { get; set; } = new();
    }

    private class OllamaModelItem
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("size")]
        public long Size { get; set; }

        [JsonPropertyName("details")]
        public OllamaModelDetails? Details { get; set; }
    }

    private class OllamaModelDetails
    {
        [JsonPropertyName("parameter_size")]
        public string? ParameterSize { get; set; }
    }
}
