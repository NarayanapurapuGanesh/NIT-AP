using System.Security.Claims;
using FacultyIQ.Domain.Entities.Identity;

namespace FacultyIQ.Application.Abstractions.Identity;

public interface ITokenService
{
    string GenerateAccessToken(User user, IEnumerable<string> roles, IEnumerable<string> permissions);
    RefreshToken GenerateRefreshToken(Guid userId, string? ipAddress);
    ClaimsPrincipal? GetPrincipalFromExpiredToken(string token);
}
