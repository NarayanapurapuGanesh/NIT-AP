using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.Extensions.Logging;
using FacultyIQ.Application.Abstractions.Data;
using FacultyIQ.Application.Abstractions.Interaction;
using FacultyIQ.Domain.Entities.Interaction;
using FacultyIQ.SharedKernel;
using Microsoft.EntityFrameworkCore;

namespace FacultyIQ.Infrastructure.Services;

/// <summary>
/// Core orchestrator service for teaching interaction sessions.
/// Coordinates between the domain layer, Python AI service, persistence, and SignalR.
/// </summary>
public class InteractionSessionService : IInteractionSessionService
{
    private readonly IApplicationDbContext _dbContext;
    private readonly IUnitOfWork _unitOfWork;
    private readonly IInteractionAIClient _aiClient;
    private readonly ILogger<InteractionSessionService> _logger;

    public InteractionSessionService(
        IApplicationDbContext dbContext,
        IUnitOfWork unitOfWork,
        IInteractionAIClient aiClient,
        ILogger<InteractionSessionService> logger)
    {
        _dbContext = dbContext;
        _unitOfWork = unitOfWork;
        _aiClient = aiClient;
        _logger = logger;
    }

    public async Task<Result<StartInteractionResponse>> StartSessionAsync(
        StartInteractionRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            // Determine persona (override or auto-select)
            var personaType = request.PersonaOverride ?? PersonaType.Curious;
            var persona = StudentPersona.GetDefault(personaType);

            // Create the session aggregate
            var session = InteractionSession.Create(
                request.CandidateApplicationId,
                personaType,
                request.Subject,
                request.Department,
                request.MaxTurns,
                request.FacultyContextJson);

            session.Start();

            // Persist the session
            _dbContext.InteractionSessions.Add(session);

            // Generate opening message from the AI service
            // We call the Python service to get the first student message
            var openingResult = await GenerateOpeningMessageAsync(
                personaType.ToString(), request.Subject, request.Department, cancellationToken);

            string openingMessage = openingResult ?? $"Hi, I'm having trouble understanding {request.Subject}. Can you help me?";

            // Add the opening turn
            var turn = session.AddTurn(SpeakerRole.Student, openingMessage);
            _dbContext.ConversationTurns.Add(turn);

            // Record initial Bloom progress
            var bloomEntry = BloomProgressEntry.Create(
                session.Id, 0, BloomLevel.Remember, persona.StartingBloomLevel,
                request.Subject, "Session initialized");
            _dbContext.BloomProgressEntries.Add(bloomEntry);

            await _unitOfWork.SaveChangesAsync(cancellationToken);

            _logger.LogInformation(
                "[Interaction] Session {SessionId} started for candidate {CandidateId} with {Persona} persona",
                session.Id, request.CandidateApplicationId, personaType);

            return Result.Success(new StartInteractionResponse(
                session.Id,
                persona.Name,
                personaType,
                openingMessage,
                persona.StartingBloomLevel,
                request.Subject));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "[Interaction] Failed to start session");
            return Result.Failure<StartInteractionResponse>(
                Error.Unexpected("Interaction.StartFailed", ex.Message));
        }
    }

    public async Task<Result<StudentResponseResult>> ProcessFacultyMessageAsync(
        FacultyMessageRequest request,
        CancellationToken cancellationToken = default)
    {
        try
        {
            var session = await _dbContext.InteractionSessions
                .Include(s => s.ConversationTurns.OrderBy(t => t.TurnNumber))
                .Include(s => s.Misconceptions)
                .Include(s => s.EvidencePackets)
                .Include(s => s.BloomProgress)
                .FirstOrDefaultAsync(s => s.Id == request.SessionId, cancellationToken);

            if (session is null)
                return Result.Failure<StudentResponseResult>(
                    Error.NotFound("Interaction.NotFound", "Session not found"));

            if (session.Status != SessionStatus.Active)
                return Result.Failure<StudentResponseResult>(
                    Error.Unexpected("Interaction.NotActive", $"Session is in {session.Status} state"));

            // Add the faculty message as a turn
            var facultyTurn = session.AddTurn(SpeakerRole.Faculty, request.Message);
            _dbContext.ConversationTurns.Add(facultyTurn);

            // Build the AI request
            var aiRequest = BuildAIRequest(session, request.Message);

            // Call the Python AI service
            var aiResult = await _aiClient.GenerateStudentResponseAsync(aiRequest, cancellationToken);
            if (aiResult.IsFailure)
            {
                _logger.LogWarning("[Interaction] AI service failed: {Error}", aiResult.Error.Description);
                // Graceful degradation: generate a simple follow-up
                var fallbackMessage = "Can you explain that a bit more? I want to make sure I understand.";
                var fallbackTurn = session.AddTurn(SpeakerRole.Student, fallbackMessage);
                _dbContext.ConversationTurns.Add(fallbackTurn);
                await _unitOfWork.SaveChangesAsync(cancellationToken);

                return Result.Success(new StudentResponseResult(
                    fallbackMessage, session.TurnCount, session.CurrentBloomLevel,
                    session.CurrentDifficulty, session.HasReachedTurnLimit(),
                    BuildAnalyticsSnapshot(session)));
            }

            var aiResponse = aiResult.Value;

            // Add the student response turn
            var studentTurn = session.AddTurn(SpeakerRole.Student, aiResponse.StudentMessage);
            _dbContext.ConversationTurns.Add(studentTurn);

            // Process teaching evaluation
            if (aiResponse.Evaluation is not null)
            {
                var metricsJson = JsonSerializer.Serialize(aiResponse.Evaluation);
                facultyTurn.SetMetricsSnapshot(metricsJson, (decimal?)aiResponse.UnderstandingEstimate);

                // Create evidence packet
                var avgScore = ((decimal)aiResponse.Evaluation.ConceptClarity +
                               (decimal)aiResponse.Evaluation.TechnicalAccuracy +
                               (decimal)aiResponse.Evaluation.QuestionHandling) / 3m;
                var evidence = session.AddEvidence(
                    facultyTurn.Id,
                    "teaching_quality",
                    avgScore,
                    aiResponse.Evaluation.EvidenceJustification,
                    (decimal)aiResponse.Evaluation.Confidence,
                    metricsJson);
                _dbContext.EvidencePackets.Add(evidence);
            }

            // Process Bloom level change
            if (aiResponse.NewBloomLevel is not null &&
                Enum.TryParse<BloomLevel>(aiResponse.NewBloomLevel, out var newBloom))
            {
                session.AdvanceBloomLevel(newBloom,
                    aiResponse.CurrentTopic ?? session.Subject,
                    aiResponse.BloomTransitionReason);
            }

            // Process new misconception
            if (aiResponse.NewMisconception is not null)
            {
                var misconception = session.AddMisconception(
                    aiResponse.NewMisconception.MisconceptionText,
                    aiResponse.NewMisconception.CorrectConcept,
                    aiResponse.NewMisconception.SubjectCategory);
                _dbContext.MisconceptionRecords.Add(misconception);
            }

            // Process misconception correction
            if (aiResponse.MisconceptionCorrection is not null)
            {
                var active = session.Misconceptions
                    .FirstOrDefault(m => m.Status == MisconceptionStatus.Presented &&
                                        m.MisconceptionText == aiResponse.MisconceptionCorrection.MisconceptionText);
                if (active is not null)
                {
                    if (aiResponse.MisconceptionCorrection.FullyCorrected)
                        active.MarkCorrected(session.TurnCount,
                            aiResponse.MisconceptionCorrection.CorrectionText,
                            (decimal)aiResponse.MisconceptionCorrection.CorrectionQuality);
                    else
                        active.MarkPartiallyCorrected(session.TurnCount,
                            aiResponse.MisconceptionCorrection.CorrectionText,
                            (decimal)aiResponse.MisconceptionCorrection.CorrectionQuality);
                }
            }

            // Check if session should end
            bool sessionComplete = aiResponse.ShouldEndSession || session.HasReachedTurnLimit();
            if (sessionComplete)
            {
                session.Complete();
            }

            await _unitOfWork.SaveChangesAsync(cancellationToken);

            return Result.Success(new StudentResponseResult(
                aiResponse.StudentMessage,
                session.TurnCount,
                session.CurrentBloomLevel,
                session.CurrentDifficulty,
                sessionComplete,
                BuildAnalyticsSnapshot(session)));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "[Interaction] Failed to process faculty message for session {SessionId}",
                request.SessionId);
            return Result.Failure<StudentResponseResult>(
                Error.Unexpected("Interaction.ProcessFailed", ex.Message));
        }
    }

    public async Task<Result> PauseSessionAsync(Guid sessionId, CancellationToken cancellationToken = default)
    {
        var session = await _dbContext.InteractionSessions.FindAsync(new object[] { sessionId }, cancellationToken);
        if (session is null)
            return Result.Failure(Error.NotFound("Interaction.NotFound", "Session not found"));

        session.Pause();
        await _unitOfWork.SaveChangesAsync(cancellationToken);
        return Result.Success();
    }

    public async Task<Result> ResumeSessionAsync(Guid sessionId, CancellationToken cancellationToken = default)
    {
        var session = await _dbContext.InteractionSessions.FindAsync(new object[] { sessionId }, cancellationToken);
        if (session is null)
            return Result.Failure(Error.NotFound("Interaction.NotFound", "Session not found"));

        session.Resume();
        await _unitOfWork.SaveChangesAsync(cancellationToken);
        return Result.Success();
    }

    public async Task<Result<InteractionSessionReport>> EndSessionAsync(
        Guid sessionId, CancellationToken cancellationToken = default)
    {
        var session = await _dbContext.InteractionSessions
            .Include(s => s.ConversationTurns.OrderBy(t => t.TurnNumber))
            .Include(s => s.Misconceptions)
            .Include(s => s.EvidencePackets)
            .Include(s => s.BloomProgress)
            .FirstOrDefaultAsync(s => s.Id == sessionId, cancellationToken);

        if (session is null)
            return Result.Failure<InteractionSessionReport>(
                Error.NotFound("Interaction.NotFound", "Session not found"));

        if (session.Status == SessionStatus.Active || session.Status == SessionStatus.Paused)
            session.Complete();

        // Generate final evaluation
        var history = session.ConversationTurns.Select(t => new ConversationMessage(
            t.Speaker.ToString(), t.Content, t.TurnNumber)).ToList();

        var evalResult = await _aiClient.GenerateFinalEvaluationAsync(
            sessionId.ToString(), history, session.FacultyContextJson ?? "", cancellationToken);

        if (evalResult.IsSuccess)
        {
            var report = evalResult.Value;
            session.SetEvaluationResults(
                (decimal)report.Scores.Teaching,
                (decimal)report.Scores.Communication,
                (decimal)report.Scores.Engagement,
                (decimal)report.Scores.StudentSatisfaction,
                (decimal)report.Scores.LearningGain,
                (decimal)report.Scores.BloomCoverage,
                (decimal)report.OverallTeachingEffectiveness,
                (decimal)report.Confidence,
                JsonSerializer.Serialize(report),
                JsonSerializer.Serialize(report.Strengths),
                JsonSerializer.Serialize(report.Weaknesses),
                JsonSerializer.Serialize(report.Recommendations));

            await _unitOfWork.SaveChangesAsync(cancellationToken);
            return Result.Success(report);
        }

        // Fallback if AI evaluation fails
        await _unitOfWork.SaveChangesAsync(cancellationToken);
        return Result.Success(BuildLocalReport(session));
    }

    public async Task<Result<InteractionSessionReport>> GetSessionReportAsync(
        Guid sessionId, CancellationToken cancellationToken = default)
    {
        var session = await _dbContext.InteractionSessions
            .Include(s => s.ConversationTurns.OrderBy(t => t.TurnNumber))
            .Include(s => s.Misconceptions)
            .Include(s => s.EvidencePackets)
            .Include(s => s.BloomProgress)
            .FirstOrDefaultAsync(s => s.Id == sessionId, cancellationToken);

        if (session is null)
            return Result.Failure<InteractionSessionReport>(
                Error.NotFound("Interaction.NotFound", "Session not found"));

        if (session.FinalReportJson is not null)
        {
            var report = JsonSerializer.Deserialize<InteractionSessionReport>(session.FinalReportJson);
            if (report is not null)
                return Result.Success(report);
        }

        return Result.Success(BuildLocalReport(session));
    }

    public async Task<Result<InteractionAnalyticsSnapshot>> GetSessionAnalyticsAsync(
        Guid sessionId, CancellationToken cancellationToken = default)
    {
        var session = await _dbContext.InteractionSessions
            .Include(s => s.ConversationTurns)
            .Include(s => s.Misconceptions)
            .Include(s => s.EvidencePackets)
            .Include(s => s.BloomProgress)
            .FirstOrDefaultAsync(s => s.Id == sessionId, cancellationToken);

        if (session is null)
            return Result.Failure<InteractionAnalyticsSnapshot>(
                Error.NotFound("Interaction.NotFound", "Session not found"));

        return Result.Success(BuildAnalyticsSnapshot(session));
    }

    // ─── Private Helpers ─────────────────────────────────────────

    private AIInteractionRequest BuildAIRequest(InteractionSession session, string facultyMessage)
    {
        var history = session.ConversationTurns
            .OrderBy(t => t.TurnNumber)
            .Select(t => new ConversationMessage(t.Speaker.ToString(), t.Content, t.TurnNumber))
            .ToList();

        var activeMisconceptions = session.Misconceptions
            .Where(m => m.Status == MisconceptionStatus.Presented || m.Status == MisconceptionStatus.Identified)
            .Select(m => new ActiveMisconception(m.MisconceptionText, m.CorrectConcept, m.Status.ToString()))
            .ToList();

        return new AIInteractionRequest(
            session.Id.ToString(),
            facultyMessage,
            session.PersonaType.ToString(),
            session.Subject,
            session.Department,
            session.TurnCount,
            session.MaxTurns,
            session.CurrentBloomLevel.ToString(),
            session.CurrentDifficulty.ToString(),
            history,
            activeMisconceptions,
            session.FacultyContextJson);
    }

    private InteractionAnalyticsSnapshot BuildAnalyticsSnapshot(InteractionSession session)
    {
        var bloomDist = session.BloomProgress
            .GroupBy(b => b.CurrentLevel.ToString())
            .ToDictionary(g => g.Key, g => g.Count());

        var totalMisconceptions = session.Misconceptions.Count;
        var corrected = session.Misconceptions.Count(m => m.Status == MisconceptionStatus.Corrected);
        var missed = session.Misconceptions.Count(m => m.Status == MisconceptionStatus.Missed);

        // Calculate running average scores from evidence
        var evidenceScores = session.EvidencePackets.Where(e => e.EvidenceType == "teaching_quality").ToList();
        var avgTeaching = evidenceScores.Any() ? evidenceScores.Average(e => e.Score) : 0.5m;

        var lastTurn = session.ConversationTurns.OrderByDescending(t => t.TurnNumber).FirstOrDefault();
        var understanding = lastTurn?.UnderstandingEstimate ?? 0.3m;

        return new InteractionAnalyticsSnapshot(
            TeachingScore: avgTeaching,
            CommunicationScore: avgTeaching * 0.9m, // Approximation until per-dimension tracking
            EngagementScore: avgTeaching * 1.05m > 1m ? 1m : avgTeaching * 1.05m,
            StudentSatisfaction: understanding * 0.95m,
            LearningGain: understanding,
            CurrentBloomLevel: session.CurrentBloomLevel,
            TurnNumber: session.TurnCount,
            MaxTurns: session.MaxTurns,
            CurrentTopic: session.Subject,
            BloomDistribution: bloomDist,
            TotalMisconceptions: totalMisconceptions,
            CorrectedMisconceptions: corrected,
            MissedMisconceptions: missed,
            TotalEvidencePackets: session.EvidencePackets.Count,
            UnderstandingEstimate: understanding);
    }

    private InteractionSessionReport BuildLocalReport(InteractionSession session)
    {
        var analytics = BuildAnalyticsSnapshot(session);

        return new InteractionSessionReport(
            SessionId: session.Id,
            CandidateApplicationId: session.CandidateApplicationId,
            OverallTeachingEffectiveness: session.OverallEffectivenessScore ?? analytics.TeachingScore,
            Scores: new InteractionScores(
                session.TeachingScore ?? analytics.TeachingScore,
                session.CommunicationScore ?? analytics.CommunicationScore,
                session.EngagementScore ?? analytics.EngagementScore,
                session.StudentSatisfactionScore ?? analytics.StudentSatisfaction,
                session.LearningGainScore ?? analytics.LearningGain,
                session.BloomCoverageScore ?? 0.5m),
            BloomDistribution: analytics.BloomDistribution,
            Strengths: session.StrengthsJson is not null
                ? JsonSerializer.Deserialize<List<string>>(session.StrengthsJson) ?? new()
                : new(),
            Weaknesses: session.WeaknessesJson is not null
                ? JsonSerializer.Deserialize<List<string>>(session.WeaknessesJson) ?? new()
                : new(),
            Evidence: session.EvidencePackets.Select(e => new EvidenceSummary(
                e.TurnNumber, e.EvidenceType, e.Score, e.Justification, e.Confidence)).ToList(),
            Recommendations: session.RecommendationsJson is not null
                ? JsonSerializer.Deserialize<List<string>>(session.RecommendationsJson) ?? new()
                : new(),
            Confidence: session.Confidence ?? 0.5m,
            TotalTurns: session.TurnCount,
            Duration: session.TotalDuration?.ToString(@"hh\:mm\:ss") ?? "00:00:00",
            PersonaUsed: session.PersonaType.ToString(),
            Subject: session.Subject,
            Department: session.Department);
    }

    private async Task<string?> GenerateOpeningMessageAsync(
        string personaType, string subject, string department, CancellationToken ct)
    {
        try
        {
            var request = new { persona_type = personaType, subject, department };
            var response = await _aiClient.IsAvailableAsync(ct) ? null : (string?)null;

            // Direct HTTP call for opening message
            using var httpClient = new HttpClient { BaseAddress = new Uri("http://localhost:8020") };
            var httpResponse = await httpClient.PostAsJsonAsync("/api/interaction/opening", request, ct);
            if (httpResponse.IsSuccessStatusCode)
            {
                var result = await httpResponse.Content.ReadFromJsonAsync<OpeningMessageResult>(ct);
                return result?.StudentMessage;
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "[Interaction] Failed to generate AI opening message, using fallback");
        }
        return null;
    }

    private record OpeningMessageResult(string StudentMessage);
}
