namespace FacultyIQ.Application.Options;

public class JwtOptions
{
    public const string SectionName = "Jwt";
    public string Issuer { get; set; } = "FacultyIQ.Api";
    public string Audience { get; set; } = "FacultyIQ.Web";
    public string SecretKey { get; set; } = "FacultyIQ_Enterprise_Super_Secret_JWT_Key_2026_Must_Be_Long_Enough!";
    public int AccessTokenExpirationMinutes { get; set; } = 15;
    public int RefreshTokenExpirationDays { get; set; } = 7;
}
