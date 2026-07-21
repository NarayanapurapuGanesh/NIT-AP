using System.Linq.Expressions;
using Microsoft.EntityFrameworkCore;
using FacultyIQ.Application.Abstractions.Data;
using FacultyIQ.Domain.Abstractions;
using FacultyIQ.Persistence.Context;
using FacultyIQ.SharedKernel;

namespace FacultyIQ.Persistence.Repositories;

public class GenericRepository<TKey, TEntity> : IGenericRepository<TKey, TEntity>
    where TKey : notnull
    where TEntity : BaseEntity<TKey>
{
    protected readonly ApplicationDbContext DbContext;
    protected readonly DbSet<TEntity> DbSet;

    public GenericRepository(ApplicationDbContext dbContext)
    {
        DbContext = dbContext;
        DbSet = dbContext.Set<TEntity>();
    }

    public virtual async Task<TEntity?> GetByIdAsync(TKey id, CancellationToken cancellationToken = default)
    {
        return await DbSet.FindAsync(new object[] { id }, cancellationToken);
    }

    public virtual async Task<IReadOnlyList<TEntity>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        return await DbSet.ToListAsync(cancellationToken);
    }

    public virtual async Task<IReadOnlyList<TEntity>> FindAsync(Expression<Func<TEntity, bool>> predicate, CancellationToken cancellationToken = default)
    {
        return await DbSet.Where(predicate).ToListAsync(cancellationToken);
    }

    public virtual async Task<PagedList<TEntity>> GetPagedAsync(
        int pageIndex,
        int pageSize,
        Expression<Func<TEntity, bool>>? predicate = null,
        CancellationToken cancellationToken = default)
    {
        IQueryable<TEntity> query = DbSet;

        if (predicate is not null)
        {
            query = query.Where(predicate);
        }

        var totalCount = await query.LongCountAsync(cancellationToken);
        var items = await query
            .Skip((pageIndex - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync(cancellationToken);

        return new PagedList<TEntity>(items, pageIndex, pageSize, totalCount);
    }

    public virtual async Task AddAsync(TEntity entity, CancellationToken cancellationToken = default)
    {
        await DbSet.AddAsync(entity, cancellationToken);
    }

    public virtual void Update(TEntity entity)
    {
        DbSet.Update(entity);
    }

    public virtual void Remove(TEntity entity)
    {
        DbSet.Remove(entity);
    }
}

public class GenericRepository<TEntity> : GenericRepository<Guid, TEntity>, IGenericRepository<TEntity>
    where TEntity : BaseEntity<Guid>
{
    public GenericRepository(ApplicationDbContext dbContext) : base(dbContext) { }
}
