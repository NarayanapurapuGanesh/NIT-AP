using Microsoft.AspNetCore.SignalR;
using System.Threading.Tasks;

namespace FacultyIQ.Api.Hubs;

public class CodingHub : Hub
{
    // Clients will join a group based on their SubmissionId or SessionId
    public async Task JoinSession(string sessionId)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, sessionId);
    }

    public async Task LeaveSession(string sessionId)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, sessionId);
    }
}
