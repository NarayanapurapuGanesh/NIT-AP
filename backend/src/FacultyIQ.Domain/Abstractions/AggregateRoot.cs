namespace FacultyIQ.Domain.Abstractions;

public abstract class AggregateRoot<TKey> : BaseEntity<TKey>
    where TKey : notnull
{
    private readonly List<IDomainEvent> _domainEvents = new();

    protected AggregateRoot(TKey id) : base(id) { }
    protected AggregateRoot() { }

    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    public void AddDomainEvent(IDomainEvent domainEvent)
    {
        _domainEvents.Add(domainEvent);
    }

    public void RemoveDomainEvent(IDomainEvent domainEvent)
    {
        _domainEvents.Remove(domainEvent);
    }

    public void ClearDomainEvents()
    {
        _domainEvents.Clear();
    }
}

public abstract class AggregateRoot : AggregateRoot<Guid>
{
    protected AggregateRoot(Guid id) : base(id) { }
    protected AggregateRoot() : base(Guid.NewGuid()) { }
}
