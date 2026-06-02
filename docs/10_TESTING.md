# 10 · Testing Strategy & Definition of Done

## Definition of Done (every increment)
An increment is **DONE** only when all are true:
1. Deliverables in `08_INCREMENT_PLAN.md` are built into `src/`.
2. Acceptance criteria pass (demonstrated, not asserted).
3. Automated tests exist and are green (see levels below).
4. Lint/format/type-check pass.
5. A validation record `increments/INC-XXX_*.md` is written (from `templates/VALIDATION_TEMPLATE.md`)
   showing what was tested and the results.
6. `09_PROGRESS.md` updated (status + %, overall recomputed).

## Test levels
| Level | Scope | Tooling |
|-------|-------|---------|
| Unit | Pure logic — each anomaly check, scoring, scoping projections, hashing | `pytest` (backend), `vitest` (frontend) |
| Integration | Endpoint + DB + service (real Postgres/Redis via compose) | `pytest` + `httpx`, test DB |
| Contract (ledger) | Anchoring to a local Fabric; Solidity tests on a local Polygon node | `hardhat test`, Fabric test network |
| E2E | Critical journeys across UI + API | Playwright |
| Security | The checklist below | manual + automated (zap baseline, dep audit) |
| Accessibility | WCAG 2.1 AA on public + Pulse | axe, Lighthouse |

## Required test fixtures (build once, reuse)
- A small **OCDS sample** with: a clean contract, a missing-signature contract, a standstill
  violation, identical-timestamp stages, a framework call-off (must NOT flag single-source), a lawful
  emergency with/without justification, related-party suppliers, an over-amended contract, a debarred
  supplier. These drive the anomaly-engine tests (INC-003/004) directly.
- A **photo fixture** with embedded GPS for Pulse capture/IPFS tests.
- A **contract PDF** for anchor/verify tests (original + 1-byte-modified copy).

## Per-area must-test cases (high value)
- **Anomaly checks:** each check has ≥1 positive and ≥1 negative fixture; false-positive safeguards
  explicitly tested (framework call-off, lawful emergency).
- **Two-tier scoping:** a public request for any contract endpoint returns **no** names / PII;
  a restricted request returns them; covered by an automated test that diffs the two projections.
- **Verification:** original → MATCH; modified → MISMATCH; unknown → "not registered".
- **Anchoring idempotency:** anchoring the same contract twice = one logical record; document bytes
  never leave the backend.
- **Offline Pulse:** simulate offline capture → queue → reconnect → exactly-once sync (Idempotency-Key).
- **Confirmation contract:** N-1 confirmations ≠ complete; Nth completes; replay/duplicate confirmer
  rejected.
- **Ghost-project:** disbursement with no completion in window → appears; matching clears it.
- **RBAC:** a table-driven test asserting every (role × permission) cell from `05_RBAC_SECURITY.md`.

## Security checklist (run at INC-019, spot-check earlier)
- [ ] All restricted endpoints reject missing/expired/invalid JWT.
- [ ] MFA required for restricted login; brute-force throttled.
- [ ] No PII or names in any `public/*` response (automated).
- [ ] No personal data written to any ledger (code review + test).
- [ ] File uploads: type/size validated, scanned, stored isolated, not executable.
- [ ] TLS enforced; secure cookies; CORS allow-list; CSP set.
- [ ] Rate limiting active on public + auth endpoints.
- [ ] Secrets only via env/vault; none in the repo (gitleaks in CI).
- [ ] Dependency audit clean (pip-audit / npm audit).
- [ ] Audit log captures every privileged action; batch anchored.

## CI gate (INC-020)
PRs must pass: lint + type-check + unit + integration + build. E2E + accessibility run on main/nightly.
