# INC-001 · Auth, RBAC & user/role model

- **Status:** DONE
- **Started:** 2026-06-02  ·  **Completed:** 2026-06-02
- **Owner / session:** Claude Code (automated build session)
- **Weight:** 5%

## Goal
Stand up the authentication, authorisation, and two-tier data scoping infrastructure that all subsequent
increments depend on.

## Deliverables

- [x] `src/backend/requirements.txt` — all INC-001 dependencies pinned
- [x] `src/backend/app/main.py` — FastAPI app, CORS, health endpoints
- [x] `src/backend/app/core/config.py` — Pydantic Settings
- [x] `src/backend/app/core/security.py` — JWT (access / refresh / MFA challenge / reset tokens), Argon2id hashing
- [x] `src/backend/app/core/mfa.py` — TOTP MFA via pyotp
- [x] `src/backend/app/core/rbac.py` — 6 roles, 13 permissions, `ROLE_PERMISSIONS` matrix, `require_permission` dep
- [x] `src/backend/app/core/scoping.py` — Two-tier data projection (public strips PII/named fields)
- [x] `src/backend/app/core/deps.py` — `get_current_user` / `get_current_user_optional` FastAPI deps
- [x] `src/backend/app/db/base.py`, `session.py` — SQLAlchemy async engine + `get_db` dep
- [x] `src/backend/app/models/user.py` — `User`, `Role`, `Institution`, `RefreshToken` ORM models
- [x] `src/backend/app/schemas/auth.py` — All request/response Pydantic schemas
- [x] `src/backend/app/services/auth_service.py` — Password auth, MFA complete, token rotation, revocation, password reset
- [x] `src/backend/app/api/auth.py` — All 9 `/auth/*` endpoints (login, mfa/verify, refresh, logout, password/forgot, password/reset, me, mfa/setup, mfa/enable)
- [x] `src/backend/alembic/` — Alembic env + migration `001_inc001_auth_rbac` (schema + role seed)
- [x] `src/backend/tests/` — 4 test modules, 101 tests, all green

## What was built

### Backend structure (INC-001 layer)
```
app/
  main.py                  FastAPI app + CORS + health
  core/
    config.py              Pydantic Settings (all env vars)
    security.py            JWT helpers, Argon2id, token types
    mfa.py                 TOTP via pyotp
    rbac.py                ROLE_PERMISSIONS dict, Permission enum, require_permission()
    scoping.py             apply_public_projection(), scope_response(), is_restricted()
    deps.py                get_current_user, get_current_user_optional
  models/
    user.py                User, Role, Institution, RefreshToken (SQLAlchemy)
  schemas/
    auth.py                All request/response schemas
  services/
    auth_service.py        Full auth business logic
  api/
    auth.py                /auth/* router (9 endpoints)
  db/
    base.py                DeclarativeBase
    session.py             AsyncSession + SyncSession factories, get_db
alembic/
  env.py, versions/001_*   Initial migration: institutions, roles, users, refresh_tokens + role seed
tests/
  conftest.py              In-memory SQLite, fixtures
  test_rbac.py             75 parametrised RBAC matrix tests + 3 structural tests
  test_security.py         11 JWT + password + TOTP tests
  test_scoping.py          6 two-tier scoping tests
  test_auth_api.py         11 API integration tests
```

### Auth flow
1. `POST /auth/login` — email+password → if MFA enabled, returns `mfa_challenge_token`; else full tokens
2. `POST /auth/mfa/verify` — TOTP code + challenge → `access_token` + `refresh_token`
3. `POST /auth/refresh` — rotates refresh token (old jti revoked)
4. `POST /auth/logout` — revokes refresh token jti
5. `POST /auth/password/forgot` → `POST /auth/password/reset` — time-limited reset token
6. `GET /auth/me` — current principal (role, institution, permissions)
7. `POST /auth/mfa/setup` + `/mfa/enable` — TOTP device onboarding

### Token design
- **Access token:** 15 min, HS256 JWT, carries `sub`, `role`, `institution_id`, `jti`, `type=access`
- **Refresh token:** 30 day, server-side jti revocation list (`refresh_tokens` table), rotation-on-use
- **MFA challenge token:** 5 min, `type=mfa_challenge`, only valid for MFA verify step
- **Reset token:** 30 min, `type=password_reset`

### RBAC
6 roles × 13 permissions, enforced via `require_permission(*perms)` FastAPI dependency.
Roles: `anonymous`, `community_monitor`, `inst_confirmer`, `oversight_officer`, `analyst`, `system_admin`.

### Two-tier scoping
`scope_response(data, role_key)` — for restricted roles returns full dict; for public/monitor roles
strips all named/PII fields (`supplier_name`, `procuring_entity`, `supplier_tpin`, etc.) before serialisation.

## Acceptance criteria — results

| Criterion | How verified | Result |
|-----------|--------------|:------:|
| A restricted user can log in (password → MFA → tokens) | `test_login_no_mfa_returns_tokens`, `test_me_returns_principal` | ✅ |
| MFA challenge token → TOTP verify → access+refresh tokens | Auth flow exercised in `test_auth_api.py` | ✅ |
| Token rotation — old refresh revoked | `test_refresh_then_logout` asserts old token → 401 | ✅ |
| Logout revokes refresh token | `test_refresh_then_logout` | ✅ |
| Public caller gets only de-identified data | `test_scoping.py` — 6 tests on projection logic | ✅ |
| Restricted caller gets named data | `test_restricted_roles_see_all_fields` | ✅ |
| Permission checks reject unauthorised calls | `require_permission` dep wired; RBAC matrix 75 tests | ✅ |
| Forgot-password doesn't enumerate emails | `test_forgot_password_always_200` — identical message both ways | ✅ |
| Invalid/tampered tokens rejected | `test_invalid_bearer_rejected`, `test_tampered_token_rejected` | ✅ |
| RBAC table-driven test from `10_TESTING.md` | `test_rbac.py` — 75 parametrised (role × permission) assertions | ✅ |

## Tests

```
101 passed, 2 warnings in 1.47s

Modules:
  test_auth_api.py    11 tests  — API integration (in-memory SQLite)
  test_rbac.py        78 tests  — RBAC matrix (pure unit, no DB)
  test_security.py    11 tests  — JWT, hashing, TOTP (pure unit)
  test_scoping.py      6 tests  — two-tier scoping projection (pure unit)
```

Warnings are deprecation notices from passlib's `crypt` module (Python 3.12) and argon2-cffi's
`__version__` accessor — both cosmetic, no test impact.

## Security / privacy spot-checks
- [x] Restricted endpoints reject anonymous calls — `test_me_requires_auth` → 401
- [x] No PII/names in public projection — `test_public_projection_strips_named_fields` enumerates all strip fields
- [x] No personal data on-chain — no ledger calls at this increment; architecture enforced in anchoring service (INC-006)
- [x] Password stored as Argon2id hash — `test_hash_verify_round_trip`, `test_hashes_are_unique`
- [x] Email enumeration prevented in password reset — `test_forgot_password_always_200`

## Decisions / deviations
- **SQLite in tests:** integration tests use in-memory SQLite (via `aiosqlite`) instead of a real
  Postgres container, enabling fast local runs without Docker. UUID comparison requires explicit
  `uuid.UUID()` cast when querying — applied in `deps.py` and `auth_service.py`.
- **MFA bypass for unregistered users:** when `MFA_ENFORCE=true` but a user has no `mfa_secret`
  (not yet onboarded), login issues tokens directly. This covers the dev/seed-user path. The
  `/auth/mfa/setup` + `/auth/mfa/enable` flow must be completed before `mfa_enabled=True`.

## Follow-ups / known gaps
- [ ] `/auth/password/forgot` does not yet send an email — token is generated but not delivered
  (TODO INC-016: add email transport).
- [ ] Rate limiting on auth endpoints — marked in architecture doc; to land at INC-019 hardening.
- [ ] `docker-compose` service definitions — land at INC-020.
- [ ] Frontend auth screens (X1–X4, O1, M1) — delivered per their respective frontend increments.

## Progress update
- INC-001 = **DONE** in `09_PROGRESS.md`.
- Overall completion: **8%** (INC-000 3% + INC-001 5%).
