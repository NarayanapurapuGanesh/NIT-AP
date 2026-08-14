using System;

namespace FacultyIQ.Domain.Entities.CodingAssessment;

public abstract class Entity
{
    public Guid Id { get; protected set; }
    protected Entity(Guid id) => Id = id;
}

public class Question : Entity
{
    public string Title { get; private set; }
    public string Description { get; private set; }
    public string Constraints { get; private set; }
    public string StarterCodeJson { get; private set; } // e.g. { "python": "def solve():...", "cpp": "int main()..." }

    private Question(Guid id, string title, string description, string constraints, string starterCodeJson)
        : base(id)
    {
        Title = title;
        Description = description;
        Constraints = constraints;
        StarterCodeJson = starterCodeJson;
    }

    public static Question Create(string title, string description, string constraints, string starterCodeJson)
    {
        return new Question(Guid.NewGuid(), title, description, constraints, starterCodeJson);
    }
}
