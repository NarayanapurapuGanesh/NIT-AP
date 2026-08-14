using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using FacultyIQ.Domain.Entities.CodingAssessment;

namespace FacultyIQ.Persistence.Configurations.CodingAssessment;

public class ExecutionResultConfiguration : IEntityTypeConfiguration<ExecutionResult>
{
    public void Configure(EntityTypeBuilder<ExecutionResult> builder)
    {
        builder.HasKey(e => e.Id);
        
        builder.Property(e => e.Status)
            .HasConversion<string>()
            .HasMaxLength(50);
            
        builder.Property(e => e.Score)
            .HasColumnType("decimal(5,2)");
    }
}
