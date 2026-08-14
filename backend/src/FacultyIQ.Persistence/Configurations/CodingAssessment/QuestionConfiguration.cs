using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using FacultyIQ.Domain.Entities.CodingAssessment;

namespace FacultyIQ.Persistence.Configurations.CodingAssessment;

public class QuestionConfiguration : IEntityTypeConfiguration<Question>
{
    public void Configure(EntityTypeBuilder<Question> builder)
    {
        builder.HasKey(q => q.Id);
        
        builder.Property(q => q.Title)
            .IsRequired()
            .HasMaxLength(255);
            
        builder.Property(q => q.Description)
            .IsRequired();
            
        builder.Property(q => q.StarterCodeJson)
            .HasColumnType("jsonb");
    }
}
