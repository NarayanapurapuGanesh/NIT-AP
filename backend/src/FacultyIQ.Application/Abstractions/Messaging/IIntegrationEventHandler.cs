using System.Threading;
using System.Threading.Tasks;

namespace FacultyIQ.Application.Abstractions.Messaging;

public interface IIntegrationEventHandler<in TEvent> where TEvent : class
{
    Task HandleAsync(TEvent @event, CancellationToken cancellationToken = default);
}
