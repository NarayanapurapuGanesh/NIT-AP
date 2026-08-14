using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using FacultyIQ.Domain.Entities.CodingAssessment;

namespace FacultyIQ.Persistence.Configurations.CodingAssessment;

public class StaticAnalysisMetricsConfiguration : IEntityTypeConfiguration<StaticAnalysisMetrics>
{
    public void Configure(EntityTypeBuilder<StaticAnalysisMetrics> builder)
    {
        builder.HasKey(s => s.Id);
        
        builder.Property(s => s.MaintainabilityIndex)
            .HasColumnType("decimal(5,2)");
            
        builder.Property(s => s.SecurityFlagsJson)
            .HasColumnType("jsonb");
            
        builder.HasOne<Submission>()
            .WithOne()
            .HasForeignKey<StaticAnalysisMetrics>(s => s.SubmissionId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
