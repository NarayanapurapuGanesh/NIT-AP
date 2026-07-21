using FacultyIQ.SharedKernel.Interfaces;

namespace FacultyIQ.Infrastructure.Services;

public class DateTimeProvider : IDateTimeProvider
{
    public DateTime UtcNow => DateTime.UtcNow;
}
