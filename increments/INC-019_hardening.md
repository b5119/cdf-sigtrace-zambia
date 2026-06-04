# INC-019 · Testing, Security & Accessibility Hardening

- **Status:** DONE
- **Started:** 2026-06-05  ·  **Completed:** 2026-06-05
- **Owner / session:** Claude Code
- **Weight:** 4%

## Goal
Security hardening (headers, consolidated checklist, audit-integrity verification), accessibility
(X5 offline/error states, X6 data-protection notice), and a coverage run.

## Deliverables

### Security
- [x] `app/core/security_headers.py` — SecurityHeadersMiddleware (HSTS, CSP, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy, Permissions-Policy)
- [x] `app/services/audit_service.py` — `verify_integrity()` recomputes anchored batch hashes, detects tampering
- [x] `GET /admin/audit/verify` — audit integrity check endpoint
- [x] `tests/test_security_checklist.py` — 23 tests automating the docs/10_TESTING.md checklist

### Accessibility (public app)
- [x] **X5** `OfflineBanner.tsx` — `role="alert"` connectivity banner; existing 404/error states
- [x] **X6** `Consent.tsx` — plain-language Data Protection Notice (DPA No. 3 of 2021), linked in footer
- [x] Semantic headings, `aria-hidden` on decorative icons, focus-visible states throughout

## Security checklist — automated (23 tests)
| Checklist item | Test |
|----------------|------|
| Restricted endpoints reject missing/invalid JWT | `test_restricted_endpoints_reject_no_jwt` (7 paths), `test_restricted_endpoint_rejects_invalid_jwt` |
| No PII/names in public responses | `test_public_responses_have_no_pii_fields` (5 paths) |
| No personal data on any ledger | `test_anchor_sends_only_hash_not_document`, `test_ipfs_cid_is_hash_not_content` |
| File uploads type/size validated | `test_public_verify_rejects_non_pdf` (415), `test_public_verify_rejects_empty` (400) |
| Security headers set | `test_security_headers_present` (HSTS, CSP, X-Frame-Options, nosniff, Referrer-Policy) |
| Rate limiting active | `test_rate_limiter_configured` |
| Passwords Argon2id | `test_passwords_use_argon2` |
| Audit tamper-evidence | `test_audit_integrity_detects_tampering` (alter entry → verify fails) |
| MFA enforce flag | `test_mfa_enforce_setting_exists` |
| Two-tier isolation | `test_public_caller_gets_no_named_contract_data` |

## Test & coverage run
```
390 passed in 39s
Coverage: 75% overall (2815 stmts, 703 missed)
  Models / schemas:          94–100%
  Scoring / anomaly engine:  71–80%
  Anchor / Polygon / audit:  95–96%
  Monitor:                   81%
  Gaps: Celery task wrappers (22–25%, prod-only), some auth/case
        service branches reached only via specific flows
```

## WCAG 2.1 AA posture (public + Pulse)
- Semantic landmarks (`<nav>`, `<main>`, `<footer>`), heading hierarchy.
- Colour contrast: Integrity Green / Ink on light surfaces meets AA; risk colours paired with text labels (never colour-only).
- Keyboard: all interactive elements are native `<button>`/`<a>`/`<input>` with visible focus.
- `role="alert"` on the offline banner; `aria-hidden` on decorative icons.
- Full axe/Lighthouse audit deferred to a running-deployment pass (INC-020).

## Tests — 390/390 backend green (23 new). All three frontends type-check clean.

## Follow-ups
- Blanket audit middleware for ALL mutations → optional
- Live axe-core + Lighthouse CI pass against the running apps → INC-020
- gitleaks + pip-audit + npm audit in CI → INC-020
- Playwright E2E (login→dashboard, offline capture→sync) → INC-020

## Progress update
- INC-019 = **DONE** — Overall: **98%**.
