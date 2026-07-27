using System;
using System.Threading;
using System.Threading.Tasks;
using FacultyIQ.Application.Abstractions.Data;
using FacultyIQ.Application.Abstractions.Messaging;
using FacultyIQ.Domain.Entities.Recruitment;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Application.Features.Recruitment.Commands.UpdateStageScore;

public enum AssessmentStage
{
    ResumeValidation,
    VideoAnalysis,
    CodingTest,
    InteractionSession
}

public record UpdateStageScoreCommand(Guid ApplicationId, AssessmentStage Stage, decimal Score) : ICommand;

internal sealed class UpdateStageScoreCommandHandler : ICommandHandler<UpdateStageScoreCommand>
{
    private readonly IGenericRepository<CandidateApplication> _applicationRepository;
    private readonly IUnitOfWork _unitOfWork;

    public UpdateStageScoreCommandHandler(
        IGenericRepository<CandidateApplication> applicationRepository,
        IUnitOfWork unitOfWork)
    {
        _applicationRepository = applicationRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<Result> HandleAsync(UpdateStageScoreCommand command, CancellationToken cancellationToken = default)
    {
        var application = await _applicationRepository.GetByIdAsync(command.ApplicationId, cancellationToken);
        
        if (application == null)
            return Result.Failure(new Error("Application.NotFound", "The application was not found."));

        switch (command.Stage)
        {
            case AssessmentStage.ResumeValidation:
                application.CompleteResumeValidation(command.Score);
                break;
            case AssessmentStage.VideoAnalysis:
                application.CompleteVideoAnalysis(command.Score);
                break;
            case AssessmentStage.CodingTest:
                application.CompleteCodingTest(command.Score);
                break;
            case AssessmentStage.InteractionSession:
                application.CompleteInteractionSession(command.Score);
                break;
            default:
                return Result.Failure(new Error("Application.InvalidStage", "The provided stage is invalid."));
        }

        _applicationRepository.Update(application);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return Result.Success();
    }
}
