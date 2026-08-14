using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using FacultyIQ.Domain.Entities.CodingAssessment;

namespace FacultyIQ.Persistence.Configurations.CodingAssessment;

public class SubmissionConfiguration : IEntityTypeConfiguration<Submission>
{
    public void Configure(EntityTypeBuilder<Submission> builder)
    {
        builder.HasKey(s => s.Id);
        
        builder.Property(s => s.CandidateId)
            .IsRequired();
            
        builder.Property(s => s.Language)
            .IsRequired()
            .HasMaxLength(50);
            
        builder.Property(s => s.Status)
            .HasConversion<string>()
            .HasMaxLength(50);
            
        builder.HasOne(s => s.ExecutionResult)
            .WithOne()
            .HasForeignKey<ExecutionResult>(e => e.SubmissionId)
            .OnDelete(DeleteBehavior.Cascade);
            
        builder.HasOne(s => s.AiEvaluation)
            .WithOne()
            .HasForeignKey<AiEvaluation>(a => a.SubmissionId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
