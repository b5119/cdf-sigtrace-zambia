# 05 · RBAC & Security Architecture

See `schematics/rbac_matrix.png` for the visual permission matrix.

## 1. Roles (role-based model)
| Role key | Who | Tier | Summary |
|----------|-----|------|---------|
| `anonymous` | Any citizen / journalist | Public | Read aggregated/de-identified data; verify a contract document |
| `community_monitor` | Vetted CDF field monitor | Restricted (field) | Create field submissions; see own submissions; offline |
| `inst_confirmer` | Institutional confirmer (e.g. council/ward officer) | Restricted | Confirm/reject field submissions (multi-party) |
| `oversight_officer` | OAG / ACC / ZPPA officer | Restricted | Read named contract data; review & action anomalies; cases; ghost-project queue |
| `analyst` | Oversight analyst | Restricted | Read named data + analytics/network tools; no actioning |
| `system_admin` | Platform administrator | Restricted | Users, weights/thresholds, ingestion, ledger nodes, audit, health |

Notes:
- `oversight_officer` and `analyst` are **institution-scoped** — they see data per their institution's
  data-sharing agreement.
- `inst_confirmer` is often an additional permission held alongside `community_monitor` or a council role.
- Roles are data (`Role.permissions jsonb`) so they can be tuned without code changes.

## 2. Permission matrix (resource × role)
✓ = allowed. Enforced centrally (see §4).

| Permission | anon | monitor | confirmer | officer | analyst | admin |
|------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Read public aggregates | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Verify a document (hash check) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Read **named** contract data | | | ✓ | ✓ | ✓ | ✓ |
| Review / action anomalies | | | | ✓ | | ✓ |
| Create field submission | | ✓ | | | | |
| Confirm / reject submission | | | ✓ | ✓ | | ✓ |
| Ghost-project actions (open case/escalate) | | | ✓ | ✓ | | ✓ |
| Case management | | | | ✓ | | ✓ |
| Manage users & roles | | | | | | ✓ |
| Configure weights / thresholds | | | | | | ✓ |
| Ledger / node governance | | | | | | ✓ |
| Read audit log | | | | ✓ | ✓ | ✓ |

## 3. Authentication
- **Public tier:** no authentication. Read-only, aggregated data only, aggressively cached, rate-limited.
- **Restricted tier:** email + password (Argon2id hashed) **+ mandatory TOTP MFA**.
- **Tokens:** short-lived **JWT access token** (~15 min) + rotating **refresh token** (httpOnly,
  secure cookie or secure store on the PWA). Tokens carry `sub`, `role`, `institution_id`, `jti`.
- **Community monitors:** device-bound credential; refresh works offline within a grace window so the
  PWA functions without connectivity, then re-validates on sync.
- **Session controls:** refresh rotation, server-side revocation list (`jti`), forced re-auth for
  sensitive admin actions, idle + absolute timeouts.

## 4. Authorisation (how it is enforced)
Three layers, all server-side — never trust the client:
1. **Gateway/middleware** — validates JWT, attaches the principal (role, institution).
2. **Permission decorator** on each endpoint — declares the required permission(s); checked against
   the role's permission set. (See `03_API_ENDPOINTS.md` "Auth" column.)
3. **Two-tier data scoping** — a response projection layer that strips named/PII fields for non-
   restricted callers and applies institution filters. This is the single most important control: a
   public caller physically cannot receive named contract-level data, regardless of endpoint.

## 5. Security architecture (defence in depth)
**Transport & edge**
- TLS 1.3 everywhere; HSTS; secure + httpOnly + SameSite cookies; certificate pinning on the PWA.
- Rate limiting + basic WAF rules at the gateway; per-IP and per-token quotas on the public tier.

**Application**
- Input validation via Pydantic on every request; output schemas prevent over-exposure.
- CSRF protection for any cookie-authenticated state-changing request; strict CORS allow-list.
- Content Security Policy; no inline scripts; subresource integrity on the SPAs.
- File-upload safety: contract PDFs and photos are size/type-checked, virus-scanned, stored in an
  isolated object store, never executed; EXIF/GPS validated for Pulse photos.

**Data**
- Encryption at rest (DB + object store). Secrets via environment/vault, never committed.
- **Data minimisation:** collect only what each function needs.
- **PII strictly off-chain.** Ledgers hold only SHA-256 hashes and non-personal metadata.
- **Right to erasure:** because personal data is off-chain, it can be erased without touching the
  ledger; on-chain hashes are not personal data.
- Retention policy per data class; field-monitor identity access is restricted and logged.

**Ledger / crypto**
- Hyperledger Fabric identities per institution (MSP); endorsement policies for anchoring writes.
- Polygon writes go through a backend signer; the confirmation contract enforces multi-party
  confirmation before a project is marked complete.
- IPFS content addressing makes any altered photo detectable (the CID changes).

**Auditability**
- Append-only `AuditLog` for every privileged action (who/what/when/target).
- Periodic batch of the audit log is hashed and anchored to Fabric → tamper-evident audit trail.

**Privacy / ethics controls**
- Two-tier output (public de-identified / restricted named).
- All analytic outputs labelled "risk signal requiring review", never "wrongdoing".
- Named findings released only to authorised bodies under a data-sharing agreement.

## 6. Threat model (STRIDE → mitigation, abridged)
| Threat | Mitigation |
|--------|-----------|
| **S**poofing | MFA, JWT signature, device-bound monitor creds, Fabric MSP |
| **T**ampering | On-chain hashes, IPFS CIDs, append-only + anchored audit log |
| **R**epudiation | Audit log + multi-party confirmations + ledger timestamps |
| **I**nfo disclosure | Two-tier scoping, encryption at rest/in transit, PII off-chain |
| **D**enial of service | Rate limiting, caching of public tier, async queues |
| **E**levation of privilege | Central RBAC, least privilege, server-side checks, admin re-auth |
