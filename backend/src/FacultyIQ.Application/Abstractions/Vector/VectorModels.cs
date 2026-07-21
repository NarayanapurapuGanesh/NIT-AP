namespace FacultyIQ.Application.Abstractions.Vector;

public record VectorRecord(
    Guid Id,
    float[] Vector,
    IDictionary<string, object> Payload
);

public record SearchResult(
    Guid Id,
    float Score,
    IDictionary<string, object> Payload
);

public record CollectionDetails(
    string Name,
    ulong VectorsCount,
    ulong PointsCount,
    uint VectorSize,
    string DistanceMetric
);
