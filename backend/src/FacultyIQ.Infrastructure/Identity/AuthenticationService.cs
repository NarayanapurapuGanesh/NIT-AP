using Microsoft.EntityFrameworkCore;
using FacultyIQ.Application.Abstractions.Data;
using FacultyIQ.Application.Abstractions.Identity;
using FacultyIQ.Application.Features.Auth;
using FacultyIQ.Domain.Entities.Identity;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Infrastructure.Identity;

public class AuthenticationService : IAuthenticationService
{
    private readonly IApplicationDbContext _dbContext;
    private readonly IPasswordHasher _passwordHasher;
    private readonly ITokenService _tokenService;

    public AuthenticationService(
        IApplicationDbContext dbContext,
        IPasswordHasher passwordHasher,
        ITokenService tokenService)
    {
        _dbContext = dbContext;
        _passwordHasher = passwordHasher;
        _tokenService = tokenService;
    }

    public async Task<Result<AuthResponse>> LoginAsync(LoginRequest request, string? ipAddress, CancellationToken cancellationToken = default)
    {
        var user = await _dbContext.Users
            .Include(u => u.UserRoles)
                .ThenInclude(ur => ur.Role)
                    .ThenInclude(r => r.RolePermissions)
                        .ThenInclude(rp => rp.Permission)
            .FirstOrDefaultAsync(u => u.Email == request.Email && !u.IsDeleted, cancellationToken);

        if (user is null || !_passwordHasher.VerifyPassword(request.Password, user.PasswordHash))
        {
            return Result.Failure<AuthResponse>(Error.Unauthorized("Auth.InvalidCredentials", "Invalid email or password."));
        }

        if (!user.IsActive)
        {
            return Result.Failure<AuthResponse>(Error.Forbidden("Auth.AccountInactive", "User account is disabled."));
        }

        var roles = user.UserRoles.Select(ur => ur.Role.Name).ToList();
        var permissions = user.UserRoles
            .SelectMany(ur => ur.Role.RolePermissions)
            .Select(rp => rp.Permission.Code)
            .Distinct()
            .ToList();

        var accessToken = _tokenService.GenerateAccessToken(user, roles, permissions);
        var refreshToken = _tokenService.GenerateRefreshToken(user.Id, ipAddress);

        user.RefreshTokens.Add(refreshToken);
        await _dbContext.SaveChangesAsync(cancellationToken);

        var userDto = new UserDto(
            user.Id,
            user.Email,
            user.Username,
            user.FirstName,
            user.LastName,
            user.IsActive,
            roles,
            permissions
        );

        return Result.Success(new AuthResponse(accessToken, refreshToken.Token, refreshToken.ExpiresAtUtc, userDto));
    }

    public async Task<Result<AuthResponse>> RegisterAsync(RegisterRequest request, string? ipAddress, CancellationToken cancellationToken = default)
    {
        var emailExists = await _dbContext.Users.AnyAsync(u => u.Email == request.Email, cancellationToken);
        if (emailExists)
        {
            return Result.Failure<AuthResponse>(Error.Conflict("Auth.EmailExists", "User with this email already exists."));
        }

        var roleName = string.IsNullOrWhiteSpace(request.RoleName) ? "Applicant" : request.RoleName;
        var role = await _dbContext.Roles.FirstOrDefaultAsync(r => r.Name == roleName, cancellationToken);
        if (role is null)
        {
            return Result.Failure<AuthResponse>(Error.NotFound("Auth.RoleNotFound", $"Specified role '{roleName}' was not found."));
        }

        var user = new User
        {
            Id = Guid.NewGuid(),
            Email = request.Email,
            Username = request.Email,
            FirstName = request.FirstName,
            LastName = request.LastName,
            PasswordHash = _passwordHasher.HashPassword(request.Password),
            IsActive = true,
            EmailConfirmed = false
        };

        user.UserRoles.Add(new UserRole { User = user, Role = role });

        _dbContext.Users.Add(user);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return await LoginAsync(new LoginRequest(request.Email, request.Password), ipAddress, cancellationToken);
    }

    public async Task<Result<AuthResponse>> RefreshTokenAsync(RefreshTokenRequest request, string? ipAddress, CancellationToken cancellationToken = default)
    {
        var principal = _tokenService.GetPrincipalFromExpiredToken(request.AccessToken);
        if (principal is null)
        {
            return Result.Failure<AuthResponse>(Error.Unauthorized("Auth.InvalidAccessToken", "Invalid access token."));
        }

        var userIdClaim = principal.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;
        if (!Guid.TryParse(userIdClaim, out var userId))
        {
            return Result.Failure<AuthResponse>(Error.Unauthorized("Auth.InvalidUserClaim", "Invalid user claim in token."));
        }

        var user = await _dbContext.Users
            .Include(u => u.RefreshTokens)
            .Include(u => u.UserRoles)
                .ThenInclude(ur => ur.Role)
                    .ThenInclude(r => r.RolePermissions)
                        .ThenInclude(rp => rp.Permission)
            .FirstOrDefaultAsync(u => u.Id == userId && !u.IsDeleted, cancellationToken);

        if (user is null)
        {
            return Result.Failure<AuthResponse>(Error.NotFound("Auth.UserNotFound", "User not found."));
        }

        var existingRefreshToken = user.RefreshTokens.FirstOrDefault(t => t.Token == request.RefreshToken);
        if (existingRefreshToken is null || !existingRefreshToken.IsActive)
        {
            return Result.Failure<AuthResponse>(Error.Unauthorized("Auth.InvalidRefreshToken", "Refresh token is invalid or expired."));
        }

        // Token Rotation
        existingRefreshToken.RevokedAtUtc = DateTime.UtcNow;
        existingRefreshToken.RevokedByIp = ipAddress;

        var newRefreshToken = _tokenService.GenerateRefreshToken(user.Id, ipAddress);
        existingRefreshToken.ReplacedByToken = newRefreshToken.Token;
        user.RefreshTokens.Add(newRefreshToken);

        var roles = user.UserRoles.Select(ur => ur.Role.Name).ToList();
        var permissions = user.UserRoles
            .SelectMany(ur => ur.Role.RolePermissions)
            .Select(rp => rp.Permission.Code)
            .Distinct()
            .ToList();

        var newAccessToken = _tokenService.GenerateAccessToken(user, roles, permissions);

        await _dbContext.SaveChangesAsync(cancellationToken);

        var userDto = new UserDto(
            user.Id,
            user.Email,
            user.Username,
            user.FirstName,
            user.LastName,
            user.IsActive,
            roles,
            permissions
        );

        return Result.Success(new AuthResponse(newAccessToken, newRefreshToken.Token, newRefreshToken.ExpiresAtUtc, userDto));
    }

    public async Task<Result> RevokeTokenAsync(string token, string? ipAddress, CancellationToken cancellationToken = default)
    {
        var refreshToken = await _dbContext.RefreshTokens
            .FirstOrDefaultAsync(t => t.Token == token, cancellationToken);

        if (refreshToken is null || !refreshToken.IsActive)
        {
            return Result.Failure(Error.NotFound("Auth.TokenNotFound", "Token not found or already revoked."));
        }

        refreshToken.RevokedAtUtc = DateTime.UtcNow;
        refreshToken.RevokedByIp = ipAddress;

        await _dbContext.SaveChangesAsync(cancellationToken);
        return Result.Success();
    }

    public async Task<Result<UserDto>> GetCurrentUserAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        var user = await _dbContext.Users
            .Include(u => u.UserRoles)
                .ThenInclude(ur => ur.Role)
                    .ThenInclude(r => r.RolePermissions)
                        .ThenInclude(rp => rp.Permission)
            .FirstOrDefaultAsync(u => u.Id == userId && !u.IsDeleted, cancellationToken);

        if (user is null)
        {
            return Result.Failure<UserDto>(Error.NotFound("Auth.UserNotFound", "User profile not found."));
        }

        var roles = user.UserRoles.Select(ur => ur.Role.Name).ToList();
        var permissions = user.UserRoles
            .SelectMany(ur => ur.Role.RolePermissions)
            .Select(rp => rp.Permission.Code)
            .Distinct()
            .ToList();

        return Result.Success(new UserDto(
            user.Id,
            user.Email,
            user.Username,
            user.FirstName,
            user.LastName,
            user.IsActive,
            roles,
            permissions
        ));
    }

    public async Task<Result> ChangePasswordAsync(Guid userId, ChangePasswordRequest request, CancellationToken cancellationToken = default)
    {
        var user = await _dbContext.Users.FirstOrDefaultAsync(u => u.Id == userId && !u.IsDeleted, cancellationToken);
        if (user is null)
        {
            return Result.Failure(Error.NotFound("Auth.UserNotFound", "User not found."));
        }

        if (!_passwordHasher.VerifyPassword(request.CurrentPassword, user.PasswordHash))
        {
            return Result.Failure(Error.Unauthorized("Auth.InvalidCurrentPassword", "Current password does not match."));
        }

        user.PasswordHash = _passwordHasher.HashPassword(request.NewPassword);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }

    public async Task<Result> UpdateProfileAsync(Guid userId, UpdateProfileRequest request, CancellationToken cancellationToken = default)
    {
        var user = await _dbContext.Users.FirstOrDefaultAsync(u => u.Id == userId && !u.IsDeleted, cancellationToken);
        if (user is null)
        {
            return Result.Failure(Error.NotFound("Auth.UserNotFound", "User not found."));
        }

        user.FirstName = request.FirstName;
        user.LastName = request.LastName;
        await _dbContext.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }
}
