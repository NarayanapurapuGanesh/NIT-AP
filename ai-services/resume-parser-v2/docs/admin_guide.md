# Enterprise Administration Platform Guide (`resume-parser-v2`)

> Phase 14 Platform providing complete Identity, Authentication, Authorization (RBAC + ABAC), Multi-Tenancy, Organization Management, User Management, Feature Flags, Configuration Center, Security Layer, Audit Administration, System Health Diagnostics, and REST APIs.

---

## 🏛️ Platform Architecture

```
               FacultyIQ Core System (Phases 1–13)
                              │
                              ▼
           [Enterprise Administration Platform]
                              │
  ┌───────────────────────────┼───────────────────────────┐
  ▼                           ▼                           ▼
[Identity & Auth Engine]    [Authorization Engine]     [Multi-Tenant Engine]
 (JWT / MFA / OAuth2)        (RBAC + ABAC Policies)    (University Isolation)
  │                           │                           │
  ├───────────────────────────┼───────────────────────────┤
  ▼                           ▼                           ▼
[User Management Engine]    [Org Structure Engine]     [Feature Flags Engine]
 (Users, Invitations)        (Campuses, Depts)         (Per-Tenant Flags)
  │                           │                           │
  ├───────────────────────────┼───────────────────────────┤
  ▼                           ▼                           ▼
[Config Center Engine]      [Security Layer Engine]    [Audit Engine]
 (Settings & Weights)        (Policies & Lockout)      (Immutable Logs)
```

---

## 👑 12 Default Configurable System Roles

| # | Role Name | Scope | Key Permissions |
|---|-----------|-------|-----------------|
| 1 | `Super Admin` | Global | Full platform permission bypass |
| 2 | `Platform Admin` | Global | Manage users, roles, tenants, settings |
| 3 | `University Admin` | Tenant | University-level user & recruitment admin |
| 4 | `HR Admin` | Tenant | Manage recruitment process & workflows |
| 5 | `Dean` | Faculty/School | High-level review and workflow approvals |
| 6 | `Department Head` | Department | Department recruitment & interviews |
| 7 | `Recruitment Committee` | Department | Search committee evaluations |
| 8 | `Faculty Reviewer` | Department | Peer resume review & candidate scoring |
| 9 | `Interviewer` | Department | Conduct candidate interviews & rubrics |
| 10 | `Observer` | Department | Read-only observation of recruitment |
| 11 | `Candidate` | Self | View application status |
| 12 | `Guest` | Minimal | Public portal access |

---

## 🔌 REST API Reference

### 1. `POST /api/v1/auth/login`
Authenticates user email/password, returning JWT access + refresh tokens.

### 2. `POST /api/v1/auth/logout`
Revokes active JWT session token.

### 3. `POST /api/v1/users`
Creates a new user account with assigned roles within a tenant.

### 4. `GET /api/v1/users`
Lists all user accounts within a tenant.

### 5. `GET /api/v1/roles`
Lists all 12 default system roles and any custom dynamic roles.

### 6. `GET /api/v1/permissions`
Lists all granular system permission definitions.

### 7. `GET /api/v1/tenants`
Lists all registered university tenants.

### 8. `GET /api/v1/organizations/tree`
Returns the full organizational hierarchy (University → Campus → Department).

### 9. `POST /api/v1/settings`
Updates global or tenant-scoped configuration parameter.

### 10. `GET /api/v1/settings`
Retrieves all system configuration key-value entries.

### 11. `GET /api/v1/feature-flags`
Lists all global feature flags and per-tenant overrides.

### 12. `GET /api/v1/audit/logs`
Queries immutable security and administrative audit trail logs.

### 13. `GET /api/v1/system/health`
Returns real-time system diagnostic metrics (workers, queues, cache, sessions).
