using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using FacultyIQ.Application.Abstractions.Data;
using FacultyIQ.Application.Options;
using FacultyIQ.Persistence.Context;
using FacultyIQ.Persistence.Interceptors;
using FacultyIQ.Persistence.Repositories;
using FacultyIQ.Persistence.Seed;

namespace FacultyIQ.Persistence;

public static class DependencyInjection
{
    public static IServiceCollection AddPersistence(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddScoped<AuditableEntityInterceptor>();
        services.AddScoped<SoftDeleteInterceptor>();

        services.AddDbContext<ApplicationDbContext>((sp, options) =>
        {
            var dbOptions = configuration.GetSection(DatabaseOptions.SectionName).Get<DatabaseOptions>() ?? new DatabaseOptions();
            var connectionString = configuration.GetConnectionString("DefaultConnection") 
                                   ?? dbOptions.ConnectionString;

            options.UseNpgsql(connectionString, npgsqlOptions =>
            {
                npgsqlOptions.MigrationsAssembly(typeof(ApplicationDbContext).Assembly.FullName);
                npgsqlOptions.EnableRetryOnFailure(dbOptions.MaxRetryCount);
                npgsqlOptions.CommandTimeout(dbOptions.CommandTimeout);
            });

            options.AddInterceptors(
                sp.GetRequiredService<AuditableEntityInterceptor>(),
                sp.GetRequiredService<SoftDeleteInterceptor>()
            );

            if (dbOptions.EnableSensitiveDataLogging) options.EnableSensitiveDataLogging();
            if (dbOptions.EnableDetailedErrors) options.EnableDetailedErrors();
        });

        services.AddScoped<IApplicationDbContext>(sp => sp.GetRequiredService<ApplicationDbContext>());
        services.AddScoped<IUnitOfWork>(sp => sp.GetRequiredService<ApplicationDbContext>());
        services.AddScoped(typeof(IGenericRepository<,>), typeof(GenericRepository<,>));
        services.AddScoped(typeof(IGenericRepository<>), typeof(GenericRepository<>));
        services.AddScoped<IDatabaseSeeder, DatabaseSeeder>();

        return services;
    }
}
