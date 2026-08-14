using System.Text.Json;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using FacultyIQ.Domain.Entities.CodingAssessment;

namespace FacultyIQ.Persistence.Configurations.CodingAssessment;

public class AiEvaluationConfiguration : IEntityTypeConfiguration<AiEvaluation>
{
    public void Configure(EntityTypeBuilder<AiEvaluation> builder)
    {
        builder.HasKey(a => a.Id);
        
        builder.Property(a => a.TeachingQualityScore)
            .HasColumnType("decimal(5,2)");
            
        builder.Property(a => a.InterviewReadinessScore)
            .HasColumnType("decimal(5,2)");
            
        builder.Property(a => a.FollowUpVivaQuestions)
            .HasConversion(
                v => JsonSerializer.Serialize(v, (JsonSerializerOptions)null),
                v => JsonSerializer.Deserialize<System.Collections.Generic.List<string>>(v, (JsonSerializerOptions)null))
            .HasColumnType("jsonb");
    }
}
