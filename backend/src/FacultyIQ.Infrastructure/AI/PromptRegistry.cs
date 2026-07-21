using FacultyIQ.Application.Abstractions.AI;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Infrastructure.AI;

public class PromptRegistry : IPromptRegistry
{
    private readonly Dictionary<string, PromptTemplate> _prompts = new()
    {
        {
            "dossier_evaluation",
            new PromptTemplate(
                "dossier_evaluation",
                "Faculty Dossier Evaluation Prompt",
                "You are an expert academic recruitment evaluator. Analyze the candidate dossier for academic rigor, grant funding, and teaching excellence.",
                "1.0.0",
                new[] { "candidate_name", "department", "publications_summary" }
            )
        },
        {
            "publication_analysis",
            new PromptTemplate(
                "publication_analysis",
                "Publication Analysis Prompt",
                "Analyze the provided academic research publication list and report h-index, citations, and major contributions.",
                "1.0.0",
                new[] { "publications_text" }
            )
        }
    };

    public Task<Result<PromptTemplate>> GetPromptTemplateAsync(string promptId, string? version = null, CancellationToken cancellationToken = default)
    {
        if (_prompts.TryGetValue(promptId, out var template))
        {
            return Task.FromResult(Result.Success(template));
        }

        return Task.FromResult(Result.Failure<PromptTemplate>(Error.NotFound("Prompt.NotFound", $"Prompt template '{promptId}' was not found.")));
    }

    public async Task<string> RenderPromptAsync(string promptId, IDictionary<string, string> variables, CancellationToken cancellationToken = default)
    {
        var templateResult = await GetPromptTemplateAsync(promptId, null, cancellationToken);
        if (templateResult.IsFailure)
        {
            throw new KeyNotFoundException($"Prompt template '{promptId}' not found.");
        }

        var text = templateResult.Value.SystemPrompt;
        foreach (var (key, value) in variables)
        {
            text = text.Replace($"{{{key}}}", value);
        }

        return text;
    }
}
