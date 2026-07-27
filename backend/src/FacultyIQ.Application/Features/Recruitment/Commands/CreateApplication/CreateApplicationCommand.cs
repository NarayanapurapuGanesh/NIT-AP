using System;
using System.Threading;
using System.Threading.Tasks;
using FacultyIQ.Application.Abstractions.Data;
using FacultyIQ.Application.Abstractions.Messaging;
using FacultyIQ.Domain.Entities.Recruitment;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Application.Features.Recruitment.Commands.CreateApplication;

public record CreateApplicationCommand(Guid CandidateId, Guid JobRequisitionId) : ICommand<Guid>;

internal sealed class CreateApplicationCommandHandler : ICommandHandler<CreateApplicationCommand, Guid>
{
    private readonly IGenericRepository<CandidateApplication> _applicationRepository;
    private readonly IUnitOfWork _unitOfWork;

    public CreateApplicationCommandHandler(
        IGenericRepository<CandidateApplication> applicationRepository,
        IUnitOfWork unitOfWork)
    {
        _applicationRepository = applicationRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<Result<Guid>> HandleAsync(CreateApplicationCommand command, CancellationToken cancellationToken = default)
    {
        var application = CandidateApplication.Create(command.CandidateId, command.JobRequisitionId);
        
        await _applicationRepository.AddAsync(application, cancellationToken);
        await _unitOfWork.SaveChangesAsync(cancellationToken);

        return Result<Guid>.Success(application.Id);
    }
}
