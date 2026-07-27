using System;
using System.Threading;
using System.Threading.Tasks;
using FacultyIQ.Application.Abstractions.Data;
using FacultyIQ.Application.Abstractions.Messaging;
using FacultyIQ.Domain.Entities.Recruitment;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Application.Features.Recruitment.Commands.GenerateFinalReport;

public record GenerateFinalReportCommand(Guid ApplicationId) : ICommand;

internal sealed class GenerateFinalReportCommandHandler : ICommandHandler<GenerateFinalReportCommand>
{
    private readonly IGenericRepository<CandidateApplication> _applicationRepository;
    private readonly IUnitOfWork _unitOfWork;

    // A real implementation might also inject an IReportGeneratorService 
    // to call the AI service and get the generated text based on scores.

    public GenerateFinalReportCommandHandler(
        IGenericRepository<CandidateApplication> applicationRepository,
        IUnitOfWork unitOfWork)
    {
        _applicationRepository = applicationRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<Result> HandleAsync(GenerateFinalReportCommand command, CancellationToken cancellationToken = default)
    {
        var application = await _applicationRepository.GetByIdAsync(command.ApplicationId, cancellationToken);
        
        if (application == null)
            return Result.Failure(new Error("Application.NotFound", "The application was not found."));

        // Dummy logic to generate report and decide acceptance based on scores
        var scores = application.Scores;
        var average = (scores.ResumeScore ?? 0) + (scores.VideoAnalysisScore ?? 0) + 
                      (scores.CodingTestScore ?? 0) + (scores.InteractionScore ?? 0);
        average /= 4m;

        bool isAccepted = average >= 70; // 70 is arbitrary pass mark
        string reportContent = $"Candidate scored an average of {average:F2}. Verdict: {(isAccepted ? "Hire" : "Reject")}.";

        application.GenerateFinalReport(reportContent, isAccepted);

        _applicationRepository.Update(application);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }
}
