using FacultyIQ.Api.Extensions;
using FacultyIQ.Api.Middleware;
using FacultyIQ.Application;
using FacultyIQ.Infrastructure;
using FacultyIQ.Infrastructure.Logging;
using FacultyIQ.Persistence;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog Logger
builder.Host.UseCustomSerilog();

// Add Clean Architecture Layers
builder.Services.AddApplication(builder.Configuration);
builder.Services.AddInfrastructure(builder.Configuration);
builder.Services.AddPersistence(builder.Configuration);

// Add API & Security Services
builder.Services.AddControllers();
builder.Services.AddCustomApiVersioning();
builder.Services.AddCustomSwagger();
builder.Services.AddCustomAuthentication(builder.Configuration);
builder.Services.AddHealthChecks();
builder.Services.AddSignalR();

// Configure CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins("http://localhost:3000", "https://localhost:3000", "http://localhost:3002", "https://localhost:3002")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

var app = builder.Build();

// Exception Handling Middleware
app.UseMiddleware<GlobalExceptionMiddleware>();

if (app.Environment.IsDevelopment())
{
    app.UseCustomSwagger();
}

app.UseHttpsRedirection();
app.UseCors("AllowFrontend");

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.MapHealthChecks("/health");
app.MapHub<FacultyIQ.Api.Hubs.CodingHub>("/hubs/coding");
app.MapHub<FacultyIQ.Api.Hubs.InteractionHub>("/hubs/interaction");

app.Run();
