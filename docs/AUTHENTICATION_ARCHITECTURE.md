# FacultyIQ Authentication & Authorization Architecture

## 🛡️ Executive Overview

FacultyIQ implements an enterprise **JWT (JSON Web Token)** authentication system with **Refresh Token Rotation**, **BCrypt** password hashing, and a dual-tier authorization framework combining **Role-Based Access Control (RBAC)** with fine-grained **Permission-Based Authorization**.

---

## 🔑 Key Components

- **BCrypt Password Hashing**: Utilizes `BCrypt.Net-Next` with a work factor of 12 for password verification.
- **Access Tokens**: Short-lived JWTs (default 15 minutes) containing user claims, role claims, and permission claims.
- **Refresh Token Rotation**: Cryptographically secure 64-byte random tokens stored in PostgreSQL. Upon refresh token usage, the existing token is revoked (`RevokedAtUtc`), and a new refresh token is issued (`ReplacedByToken`), preventing replay attacks.
- **Permission Authorization**: Custom ASP.NET Core `IAuthorizationHandler` (`PermissionAuthorizationHandler`) evaluating required permission codes (e.g., `Dossiers.Read`, `AI.Evaluate`) attached to endpoints via `[RequirePermission("...")]`.

---

## 🔐 Auth Flow Diagram

```
Client App                   FacultyIQ API                   PostgreSQL DB
    │                              │                               │
    │ ─── POST /auth/login ──────> │                               │
    │                              │ ── Query User & Password ───> │
    │                              │ <── Return Password Hash ──── │
    │                              │ Verify BCrypt Hash            │
    │                              │ Generate JWT + RefreshToken   │
    │                              │ ── Save RefreshToken ───────> │
    │ <── AuthResponse (JWT) ───── │                               │
    │                              │                               │
```

---

## 📡 API Endpoints

- `POST /api/v1/auth/login`: Authenticates credentials and returns JWT access + refresh tokens.
- `POST /api/v1/auth/register`: Registers a new user and assigns default candidate roles.
- `POST /api/v1/auth/refresh-token`: Rotates expired access token using valid refresh token.
- `POST /api/v1/auth/revoke-token`: Invalidates a refresh token.
- `GET /api/v1/auth/me`: Retrieves current authenticated user profile and active permissions.
- `POST /api/v1/auth/change-password`: Updates user password.
