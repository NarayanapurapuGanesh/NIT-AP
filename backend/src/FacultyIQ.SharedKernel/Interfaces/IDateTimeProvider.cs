namespace FacultyIQ.SharedKernel.Interfaces;

public interface IDateTimeProvider
{
    DateTime UtcNow { get; }
}
