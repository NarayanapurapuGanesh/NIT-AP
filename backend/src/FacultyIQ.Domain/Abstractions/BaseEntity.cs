namespace FacultyIQ.Domain.Abstractions;

public abstract class BaseEntity<TKey> : IEquatable<BaseEntity<TKey>>
    where TKey : notnull
{
    public TKey Id { get; set; } = default!;

    protected BaseEntity(TKey id)
    {
        Id = id;
    }

    protected BaseEntity() { }

    public bool Equals(BaseEntity<TKey>? other)
    {
        if (other is null) return false;
        if (ReferenceEquals(this, other)) return true;
        if (GetType() != other.GetType()) return false;
        return EqualityComparer<TKey>.Default.Equals(Id, other.Id);
    }

    public override bool Equals(object? obj) => Equals(obj as BaseEntity<TKey>);

    public override int GetHashCode() => EqualityComparer<TKey>.Default.GetHashCode(Id);

    public static bool operator ==(BaseEntity<TKey>? left, BaseEntity<TKey>? right) => Equals(left, right);

    public static bool operator !=(BaseEntity<TKey>? left, BaseEntity<TKey>? right) => !Equals(left, right);
}

public abstract class BaseEntity : BaseEntity<Guid>
{
    protected BaseEntity(Guid id) : base(id) { }
    protected BaseEntity() : base(Guid.NewGuid()) { }
}
