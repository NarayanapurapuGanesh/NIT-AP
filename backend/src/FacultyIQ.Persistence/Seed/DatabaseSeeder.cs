using Microsoft.EntityFrameworkCore;
using FacultyIQ.Domain.Entities.Identity;
using FacultyIQ.Persistence.Context;

namespace FacultyIQ.Persistence.Seed;

public class DatabaseSeeder : IDatabaseSeeder
{
    private readonly ApplicationDbContext _dbContext;

    public DatabaseSeeder(ApplicationDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task SeedAsync(CancellationToken cancellationToken = default)
    {
        if (await _dbContext.Roles.AnyAsync(cancellationToken))
        {
            return;
        }

        // 1. Core Permissions
        var permissions = new List<Permission>
        {
            new() { Id = Guid.NewGuid(), Code = "Users.Read", Name = "Read Users", Category = "User Management" },
            new() { Id = Guid.NewGuid(), Code = "Users.Write", Name = "Write Users", Category = "User Management" },
            new() { Id = Guid.NewGuid(), Code = "Dossiers.Read", Name = "Read Candidate Dossiers", Category = "Dossiers" },
            new() { Id = Guid.NewGuid(), Code = "Dossiers.Write", Name = "Write Candidate Dossiers", Category = "Dossiers" },
            new() { Id = Guid.NewGuid(), Code = "AI.Evaluate", Name = "Run AI Candidate Evaluation", Category = "AI Engine" },
            new() { Id = Guid.NewGuid(), Code = "System.Admin", Name = "System Administration", Category = "System" },
        };

        await _dbContext.Permissions.AddRangeAsync(permissions, cancellationToken);

        // 2. Core Roles
        var superAdminRole = new Role { Id = Guid.NewGuid(), Name = "SuperAdmin", Description = "Full Platform Administrator" };
        var uniAdminRole = new Role { Id = Guid.NewGuid(), Name = "UniversityAdmin", Description = "University Recruitment Administrator" };
        var reviewerRole = new Role { Id = Guid.NewGuid(), Name = "Reviewer", Description = "Faculty Review Committee Member" };
        var applicantRole = new Role { Id = Guid.NewGuid(), Name = "Applicant", Description = "Faculty Job Candidate" };

        var roles = new List<Role> { superAdminRole, uniAdminRole, reviewerRole, applicantRole };
        await _dbContext.Roles.AddRangeAsync(roles, cancellationToken);

        // 3. Role-Permission mappings
        foreach (var perm in permissions)
        {
            _dbContext.RolePermissions.Add(new RolePermission { Role = superAdminRole, Permission = perm });
        }

        foreach (var perm in permissions.Where(p => p.Category != "System"))
        {
            _dbContext.RolePermissions.Add(new RolePermission { Role = uniAdminRole, Permission = perm });
        }

        foreach (var perm in permissions.Where(p => p.Code is "Dossiers.Read" or "AI.Evaluate"))
        {
            _dbContext.RolePermissions.Add(new RolePermission { Role = reviewerRole, Permission = perm });
        }

        await _dbContext.SaveChangesAsync(cancellationToken);
    }
}
