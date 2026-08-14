using System.Linq.Expressions;
using System.Reflection;
using Microsoft.EntityFrameworkCore;
using FacultyIQ.Application.Abstractions.Data;
using FacultyIQ.Domain.Abstractions;
using FacultyIQ.Domain.Entities.Identity;
using FacultyIQ.Domain.Entities.Interaction;

namespace FacultyIQ.Persistence.Context;

public class ApplicationDbContext : DbContext, IApplicationDbContext, IUnitOfWork
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users => Set<User>();
    public DbSet<Role> Roles => Set<Role>();
    public DbSet<Permission> Permissions => Set<Permission>();
    public DbSet<UserRole> UserRoles => Set<UserRole>();
    public DbSet<RolePermission> RolePermissions => Set<RolePermission>();
    public DbSet<RefreshToken> RefreshTokens => Set<RefreshToken>();

    public DbSet<FacultyIQ.Domain.Entities.CodingAssessment.Question> Questions => Set<FacultyIQ.Domain.Entities.CodingAssessment.Question>();
    public DbSet<FacultyIQ.Domain.Entities.CodingAssessment.Submission> Submissions => Set<FacultyIQ.Domain.Entities.CodingAssessment.Submission>();
    public DbSet<FacultyIQ.Domain.Entities.CodingAssessment.ExecutionResult> ExecutionResults => Set<FacultyIQ.Domain.Entities.CodingAssessment.ExecutionResult>();
    public DbSet<FacultyIQ.Domain.Entities.CodingAssessment.AiEvaluation> AiEvaluations => Set<FacultyIQ.Domain.Entities.CodingAssessment.AiEvaluation>();
    public DbSet<FacultyIQ.Domain.Entities.CodingAssessment.StaticAnalysisMetrics> StaticAnalysisMetrics => Set<FacultyIQ.Domain.Entities.CodingAssessment.StaticAnalysisMetrics>();

    // Interaction Intelligence Agent
    public DbSet<InteractionSession> InteractionSessions => Set<InteractionSession>();
    public DbSet<ConversationTurn> ConversationTurns => Set<ConversationTurn>();
    public DbSet<EvidencePacket> EvidencePackets => Set<EvidencePacket>();
    public DbSet<BloomProgressEntry> BloomProgressEntries => Set<BloomProgressEntry>();
    public DbSet<MisconceptionRecord> MisconceptionRecords => Set<MisconceptionRecord>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        modelBuilder.ApplyConfigurationsFromAssembly(Assembly.GetExecutingAssembly());

        ApplySoftDeleteQueryFilters(modelBuilder);
    }

    private static void ApplySoftDeleteQueryFilters(ModelBuilder modelBuilder)
    {
        foreach (var entityType in modelBuilder.Model.GetEntityTypes())
        {
            if (typeof(ISoftDelete).IsAssignableFrom(entityType.ClrType))
            {
                var parameter = Expression.Parameter(entityType.ClrType, "e");
                var property = Expression.Property(parameter, nameof(ISoftDelete.IsDeleted));
                var falseConstant = Expression.Constant(false);
                var lambda = Expression.Lambda(Expression.Equal(property, falseConstant), parameter);

                modelBuilder.Entity(entityType.ClrType).HasQueryFilter(lambda);
            }
        }
    }
}
