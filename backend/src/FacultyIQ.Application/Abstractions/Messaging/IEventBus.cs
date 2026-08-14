using System.Threading;
using System.Threading.Tasks;

namespace FacultyIQ.Application.Abstractions.Messaging;

public interface IEventBus
{
    Task PublishAsync<T>(T @event, CancellationToken cancellationToken = default) where T : class;
}
