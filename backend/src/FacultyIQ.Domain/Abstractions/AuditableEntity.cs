namespace FacultyIQ.Domain.Abstractions;

public abstract class AuditableEntity<TKey> : AggregateRoot<TKey>
    where TKey : notnull
{
    protected AuditableEntity(TKey id) : base(id) { }
    protected AuditableEntity() { }

    public DateTime CreatedAtUtc { get; set; }
    public string? CreatedBy { get; set; }
    public DateTime? LastModifiedAtUtc { get; set; }
    public string? LastModifiedBy { get; set; }
}

public abstract class AuditableEntity : AuditableEntity<Guid>
{
    protected AuditableEntity(Guid id) : base(id) { }
    protected AuditableEntity() : base(Guid.NewGuid()) { }
}
