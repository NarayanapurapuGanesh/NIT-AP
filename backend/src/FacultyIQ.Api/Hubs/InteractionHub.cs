using Microsoft.AspNetCore.SignalR;

namespace FacultyIQ.Api.Hubs;

/// <summary>
/// SignalR hub for real-time bidirectional messaging during teaching interaction sessions.
/// Enables live student-faculty conversation and real-time analytics updates.
/// </summary>
public class InteractionHub : Hub
{
    /// <summary>
    /// Faculty joins a session group to receive student messages and analytics.
    /// </summary>
    public async Task JoinSession(string sessionId)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, $"interaction-{sessionId}");
    }

    /// <summary>
    /// Faculty leaves the session group.
    /// </summary>
    public async Task LeaveSession(string sessionId)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, $"interaction-{sessionId}");
    }

    // ─── Server → Client methods (called from the service layer) ────
    // These are invoked via IHubContext<InteractionHub> from the controller:
    //
    //   ReceiveStudentMessage(message)    — Real-time student response
    //   ReceiveAnalyticsUpdate(analytics) — Real-time metrics update
    //   SessionPaused()                   — Session paused notification
    //   SessionResumed()                  — Session resumed notification
    //   SessionEnded(report)              — Session ended with report
    //   BloomLevelChanged(level)          — Bloom level transition
    //   MisconceptionPresented(text)      — New misconception presented
    //   MisconceptionCorrected(text)      — Misconception corrected
}
