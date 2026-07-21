using Microsoft.OpenApi.Models;

namespace FacultyIQ.Api.Extensions;

public static class SwaggerExtensions
{
    public static IServiceCollection AddCustomSwagger(this IServiceCollection services)
    {
        services.AddEndpointsApiExplorer();
        services.AddSwaggerGen(c =>
        {
            c.SwaggerDoc("v1", new OpenApiInfo
            {
                Title = "FacultyIQ API",
                Version = "v1",
                Description = "Enterprise AI-Powered Faculty Recruitment Platform Web API",
                Contact = new OpenApiContact
                {
                    Name = "FacultyIQ Engineering Team",
                    Email = "support@facultyiq.edu"
                }
            });
        });

        return services;
    }

    public static IApplicationBuilder UseCustomSwagger(this IApplicationBuilder app)
    {
        app.UseSwagger();
        app.UseSwaggerUI(c =>
        {
            c.SwaggerEndpoint("/swagger/v1/swagger.json", "FacultyIQ API v1");
            c.RoutePrefix = "swagger";
        });

        return app;
    }
}
