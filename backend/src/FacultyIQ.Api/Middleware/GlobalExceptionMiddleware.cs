using System.Net;
using Microsoft.AspNetCore.Mvc;
using FacultyIQ.SharedKernel.Exceptions;

namespace FacultyIQ.Api.Middleware;

public class GlobalExceptionMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<GlobalExceptionMiddleware> _logger;

    public GlobalExceptionMiddleware(RequestDelegate next, ILogger<GlobalExceptionMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "An unhandled exception occurred during request processing. Path: {Path}", context.Request.Path);
            await HandleExceptionAsync(context, ex);
        }
    }

    private static Task HandleExceptionAsync(HttpContext context, Exception exception)
    {
        context.Response.ContentType = "application/problem+json";

        var problemDetails = exception switch
        {
            ValidationException valEx => new ProblemDetails
            {
                Title = "Validation Error",
                Status = (int)HttpStatusCode.BadRequest,
                Detail = valEx.Message,
                Instance = context.Request.Path,
                Extensions = { ["errors"] = valEx.Errors }
            },
            NotFoundException notFoundEx => new ProblemDetails
            {
                Title = "Resource Not Found",
                Status = (int)HttpStatusCode.NotFound,
                Detail = notFoundEx.Message,
                Instance = context.Request.Path
            },
            DomainException domainEx => new ProblemDetails
            {
                Title = "Domain Rule Violation",
                Status = (int)HttpStatusCode.UnprocessableEntity,
                Detail = domainEx.Message,
                Instance = context.Request.Path
            },
            _ => new ProblemDetails
            {
                Title = "An unexpected error occurred",
                Status = (int)HttpStatusCode.InternalServerError,
                Detail = "An internal server error has occurred. Please contact support if the problem persists.",
                Instance = context.Request.Path
            }
        };

        context.Response.StatusCode = problemDetails.Status ?? (int)HttpStatusCode.InternalServerError;
        return context.Response.WriteAsJsonAsync(problemDetails);
    }
}
