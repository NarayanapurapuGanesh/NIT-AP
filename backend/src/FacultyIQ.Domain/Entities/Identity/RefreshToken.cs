using FacultyIQ.Domain.Abstractions;

namespace FacultyIQ.Domain.Entities.Identity;

public class RefreshToken : BaseEntity<Guid>, ISoftDelete
{
    public Guid UserId { get; set; }
    public User User { get; set; } = null!;

    public string Token { get; set; } = string.Empty;
    public DateTime ExpiresAtUtc { get; set; }
    public DateTime CreatedAtUtc { get; set; } = DateTime.UtcNow;
    public string? CreatedByIp { get; set; }
    public DateTime? RevokedAtUtc { get; set; }
    public string? RevokedByIp { get; set; }
    public string? ReplacedByToken { get; set; }

    public bool IsActive => RevokedAtUtc == null && !IsExpired;
    public bool IsExpired => DateTime.UtcNow >= ExpiresAtUtc;

    public bool IsDeleted { get; set; }
    public DateTime? DeletedAtUtc { get; set; }
    public string? DeletedBy { get; set; }
}
