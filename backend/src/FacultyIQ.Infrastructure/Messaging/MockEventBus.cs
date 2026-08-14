using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using FacultyIQ.Application.Abstractions.Messaging;

namespace FacultyIQ.Infrastructure.Messaging;

public class MockEventBus : IEventBus
{
    private readonly ILogger<MockEventBus> _logger;

    public MockEventBus(ILogger<MockEventBus> logger)
    {
        _logger = logger;
    }

    public Task PublishAsync<T>(T @event, CancellationToken cancellationToken = default) where T : class
    {
        _logger.LogInformation("MockEventBus: Publishing event of type {EventType}: {@Event}", typeof(T).Name, @event);
        return Task.CompletedTask;
    }
}
