using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using FacultyIQ.Domain.Entities.Interaction;

namespace FacultyIQ.Persistence.Configurations;

public class InteractionSessionConfiguration : IEntityTypeConfiguration<InteractionSession>
{
    public void Configure(EntityTypeBuilder<InteractionSession> builder)
    {
        builder.ToTable("InteractionSessions");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.Subject).HasMaxLength(256).IsRequired();
        builder.Property(x => x.Department).HasMaxLength(256).IsRequired();
        builder.Property(x => x.Status).HasConversion<string>().HasMaxLength(32);
        builder.Property(x => x.PersonaType).HasConversion<string>().HasMaxLength(32);
        builder.Property(x => x.CurrentBloomLevel).HasConversion<string>().HasMaxLength(16);
        builder.Property(x => x.CurrentDifficulty).HasConversion<string>().HasMaxLength(16);
        builder.Property(x => x.FacultyContextJson).HasColumnType("jsonb");
        builder.Property(x => x.FinalReportJson).HasColumnType("jsonb");
        builder.Property(x => x.StrengthsJson).HasColumnType("jsonb");
        builder.Property(x => x.WeaknessesJson).HasColumnType("jsonb");
        builder.Property(x => x.RecommendationsJson).HasColumnType("jsonb");
        builder.Property(x => x.TeachingScore).HasPrecision(5, 4);
        builder.Property(x => x.CommunicationScore).HasPrecision(5, 4);
        builder.Property(x => x.EngagementScore).HasPrecision(5, 4);
        builder.Property(x => x.StudentSatisfactionScore).HasPrecision(5, 4);
        builder.Property(x => x.LearningGainScore).HasPrecision(5, 4);
        builder.Property(x => x.BloomCoverageScore).HasPrecision(5, 4);
        builder.Property(x => x.OverallEffectivenessScore).HasPrecision(5, 4);
        builder.Property(x => x.Confidence).HasPrecision(5, 4);

        builder.HasIndex(x => x.CandidateApplicationId);
        builder.HasIndex(x => x.Status);

        builder.HasMany(x => x.ConversationTurns)
            .WithOne(x => x.Session)
            .HasForeignKey(x => x.SessionId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(x => x.EvidencePackets)
            .WithOne(x => x.Session)
            .HasForeignKey(x => x.SessionId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(x => x.BloomProgress)
            .WithOne(x => x.Session)
            .HasForeignKey(x => x.SessionId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasMany(x => x.Misconceptions)
            .WithOne(x => x.Session)
            .HasForeignKey(x => x.SessionId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}

public class ConversationTurnConfiguration : IEntityTypeConfiguration<ConversationTurn>
{
    public void Configure(EntityTypeBuilder<ConversationTurn> builder)
    {
        builder.ToTable("ConversationTurns");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.Content).IsRequired();
        builder.Property(x => x.Speaker).HasConversion<string>().HasMaxLength(16);
        builder.Property(x => x.BloomLevel).HasConversion<string>().HasMaxLength(16);
        builder.Property(x => x.DifficultyLevel).HasConversion<string>().HasMaxLength(16);
        builder.Property(x => x.MetricsSnapshotJson).HasColumnType("jsonb");
        builder.Property(x => x.UnderstandingEstimate).HasPrecision(5, 4);

        builder.HasIndex(x => x.SessionId);
        builder.HasIndex(x => new { x.SessionId, x.TurnNumber }).IsUnique();
    }
}

public class EvidencePacketConfiguration : IEntityTypeConfiguration<EvidencePacket>
{
    public void Configure(EntityTypeBuilder<EvidencePacket> builder)
    {
        builder.ToTable("EvidencePackets");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.EvidenceType).HasMaxLength(64).IsRequired();
        builder.Property(x => x.Score).HasPrecision(5, 4);
        builder.Property(x => x.Confidence).HasPrecision(5, 4);
        builder.Property(x => x.Justification).IsRequired();
        builder.Property(x => x.BloomLevel).HasConversion<string>().HasMaxLength(16);
        builder.Property(x => x.MetricsJson).HasColumnType("jsonb");

        builder.HasIndex(x => x.SessionId);
        builder.HasIndex(x => x.ConversationTurnId);

        builder.HasOne(x => x.ConversationTurn)
            .WithMany()
            .HasForeignKey(x => x.ConversationTurnId)
            .OnDelete(DeleteBehavior.Restrict);
    }
}

public class BloomProgressEntryConfiguration : IEntityTypeConfiguration<BloomProgressEntry>
{
    public void Configure(EntityTypeBuilder<BloomProgressEntry> builder)
    {
        builder.ToTable("BloomProgressEntries");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.PreviousLevel).HasConversion<string>().HasMaxLength(16);
        builder.Property(x => x.CurrentLevel).HasConversion<string>().HasMaxLength(16);
        builder.Property(x => x.Topic).HasMaxLength(256);
        builder.Property(x => x.ProgressDirection).HasMaxLength(16);
        builder.Property(x => x.TransitionReason).HasMaxLength(512);

        builder.HasIndex(x => x.SessionId);
    }
}

public class MisconceptionRecordConfiguration : IEntityTypeConfiguration<MisconceptionRecord>
{
    public void Configure(EntityTypeBuilder<MisconceptionRecord> builder)
    {
        builder.ToTable("MisconceptionRecords");
        builder.HasKey(x => x.Id);

        builder.Property(x => x.MisconceptionText).IsRequired();
        builder.Property(x => x.CorrectConcept).IsRequired();
        builder.Property(x => x.Status).HasConversion<string>().HasMaxLength(32);
        builder.Property(x => x.CorrectionQuality).HasPrecision(5, 4);
        builder.Property(x => x.SubjectCategory).HasMaxLength(128);
        builder.Property(x => x.CorrectionText);

        builder.HasIndex(x => x.SessionId);
    }
}
