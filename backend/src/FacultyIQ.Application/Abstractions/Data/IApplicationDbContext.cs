using Microsoft.EntityFrameworkCore;
using FacultyIQ.Domain.Entities.Identity;
using FacultyIQ.Domain.Entities.Interaction;

namespace FacultyIQ.Application.Abstractions.Data;

public interface IApplicationDbContext
{
    DbSet<User> Users { get; }
    DbSet<Role> Roles { get; }
    DbSet<Permission> Permissions { get; }
    DbSet<UserRole> UserRoles { get; }
    DbSet<RolePermission> RolePermissions { get; }
    DbSet<RefreshToken> RefreshTokens { get; }

    DbSet<FacultyIQ.Domain.Entities.CodingAssessment.Question> Questions { get; }
    DbSet<FacultyIQ.Domain.Entities.CodingAssessment.Submission> Submissions { get; }
    DbSet<FacultyIQ.Domain.Entities.CodingAssessment.ExecutionResult> ExecutionResults { get; }
    DbSet<FacultyIQ.Domain.Entities.CodingAssessment.AiEvaluation> AiEvaluations { get; }
    DbSet<FacultyIQ.Domain.Entities.CodingAssessment.StaticAnalysisMetrics> StaticAnalysisMetrics { get; }

    // Interaction Intelligence Agent
    DbSet<InteractionSession> InteractionSessions { get; }
    DbSet<ConversationTurn> ConversationTurns { get; }
    DbSet<EvidencePacket> EvidencePackets { get; }
    DbSet<BloomProgressEntry> BloomProgressEntries { get; }
    DbSet<MisconceptionRecord> MisconceptionRecords { get; }

    DbSet<TEntity> Set<TEntity>() where TEntity : class;
    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
}

