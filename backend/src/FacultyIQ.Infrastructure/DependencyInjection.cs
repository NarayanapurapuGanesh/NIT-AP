using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using FacultyIQ.Application.Abstractions.AI;
using FacultyIQ.Application.Abstractions.Identity;
using FacultyIQ.Application.Abstractions.Interaction;
using FacultyIQ.Application.Abstractions.Storage;
using FacultyIQ.Application.Abstractions.Vector;
using FacultyIQ.Application.Features.Auth;
using FacultyIQ.Infrastructure.AI;
using FacultyIQ.Infrastructure.Identity;
using FacultyIQ.Infrastructure.Services;
using FacultyIQ.Infrastructure.Storage;
using FacultyIQ.Infrastructure.Vector;
using FacultyIQ.SharedKernel.Interfaces;
using FacultyIQ.Application.Abstractions.Messaging;
using FacultyIQ.Infrastructure.Messaging;

namespace FacultyIQ.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddSingleton<IDateTimeProvider, DateTimeProvider>();

        // Identity & Security Services
        services.AddSingleton<IPasswordHasher, BcryptPasswordHasher>();
        services.AddSingleton<ITokenService, JwtTokenService>();
        services.AddScoped<IAuthenticationService, AuthenticationService>();

        // Storage Infrastructure
        services.AddSingleton<MinioStorageService>();
        services.AddSingleton<IStorageService>(sp => sp.GetRequiredService<MinioStorageService>());
        services.AddSingleton<IBucketManager>(sp => sp.GetRequiredService<MinioStorageService>());
        services.AddSingleton<IStorageProvider>(sp => sp.GetRequiredService<MinioStorageService>());

        // AI Infrastructure Services
        services.AddHttpClient<OllamaClient>();
        services.AddSingleton<IOllamaClient>(sp => sp.GetRequiredService<OllamaClient>());
        services.AddSingleton<IAIService>(sp => sp.GetRequiredService<OllamaClient>());
        services.AddSingleton<IAIProvider>(sp => sp.GetRequiredService<OllamaClient>());
        services.AddSingleton<IModelRegistry, ModelRegistry>();
        services.AddSingleton<IPromptRegistry, PromptRegistry>();

        // Interaction Intelligence Agent
        services.AddHttpClient<InteractionAIClient>(client =>
        {
            var serviceUrl = configuration.GetValue<string>("InteractionAgent:ServiceUrl") ?? "http://localhost:8020";
            client.BaseAddress = new Uri(serviceUrl);
            client.Timeout = TimeSpan.FromSeconds(180);
        });
        services.AddScoped<IInteractionAIClient>(sp => sp.GetRequiredService<InteractionAIClient>());
        services.AddScoped<IInteractionSessionService, InteractionSessionService>();

        // Vector DB Services
        services.AddSingleton<QdrantVectorService>();
        services.AddSingleton<IVectorService>(sp => sp.GetRequiredService<QdrantVectorService>());
        services.AddSingleton<ICollectionManager>(sp => sp.GetRequiredService<QdrantVectorService>());

        // Messaging
        services.AddSingleton<IEventBus, MockEventBus>();

        return services;
    }
}
