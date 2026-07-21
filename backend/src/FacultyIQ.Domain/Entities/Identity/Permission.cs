using FacultyIQ.Domain.Abstractions;

namespace FacultyIQ.Domain.Entities.Identity;

public class Permission : BaseEntity<Guid>
{
    public string Code { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;

    public ICollection<RolePermission> RolePermissions { get; set; } = new List<RolePermission>();
}
