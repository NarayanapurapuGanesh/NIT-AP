namespace FacultyIQ.Application.Abstractions.AI;

public record AICompletionRequest(
    string SystemPrompt,
    string UserPrompt,
    string? Model = null,
    double Temperature = 0.2,
    int MaxTokens = 2048,
    IDictionary<string, object>? Options = null
);

public record AICompletionResponse(
    string ResponseText,
    string ModelUsed,
    int PromptTokens,
    int CompletionTokens,
    long DurationMilliseconds,
    bool IsSuccess,
    string? ErrorMessage = null
);

public record ModelMetadata(
    string Name,
    string Provider,
    long SizeBytes,
    string ParameterSize,
    bool IsAvailable
);

public record PromptTemplate(
    string Id,
    string Name,
    string SystemPrompt,
    string Version,
    IReadOnlyCollection<string> Variables
);
