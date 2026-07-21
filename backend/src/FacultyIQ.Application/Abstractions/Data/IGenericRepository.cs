using System.Linq.Expressions;
using FacultyIQ.Domain.Abstractions;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Application.Abstractions.Data;

public interface IGenericRepository<TKey, TEntity>
    where TKey : notnull
    where TEntity : BaseEntity<TKey>
{
    Task<TEntity?> GetByIdAsync(TKey id, CancellationToken cancellationToken = default);
    Task<IReadOnlyList<TEntity>> GetAllAsync(CancellationToken cancellationToken = default);
    Task<IReadOnlyList<TEntity>> FindAsync(Expression<Func<TEntity, bool>> predicate, CancellationToken cancellationToken = default);
    Task<PagedList<TEntity>> GetPagedAsync(int pageIndex, int pageSize, Expression<Func<TEntity, bool>>? predicate = null, CancellationToken cancellationToken = default);
    Task AddAsync(TEntity entity, CancellationToken cancellationToken = default);
    void Update(TEntity entity);
    void Remove(TEntity entity);
}

public interface IGenericRepository<TEntity> : IGenericRepository<Guid, TEntity>
    where TEntity : BaseEntity<Guid>
{
}
