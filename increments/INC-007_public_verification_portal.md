# INC-007 · Public Verification Portal

- **Status:** DONE
- **Started:** 2026-06-02  ·  **Completed:** 2026-06-02
- **Owner / session:** Claude Code
- **Weight:** 4%

## Goal
Implement `POST /public/verify-contract` — the public-facing verification endpoint
(screen P6). Any citizen or journalist can upload a contract PDF and learn whether
it matches the Fabric-anchored hash.

## Deliverables
- [x] `app/schemas/public.py` — PublicVerifyResponse (+ INC-008 schema stubs)
- [x] `app/api/public.py` — public router; `POST /public/verify-contract`
- [x] `tests/test_public_verify.py` — 11 tests

## Endpoint
`POST /api/v1/public/verify-contract?ocid=<ocid>` multipart PDF upload.

**Response (no named data):**
```json
{
  "verdict": "match",
  "message": "The document matches the anchored hash...",
  "provided_hash": "<sha256 of uploaded file>",
  "anchored_hash": "<sha256 stored on Fabric>",
  "ledger": "fabric",
  "ledger_tx": "<tx id>",
  "block_ref": "<block>",
  "anchored_at": "2024-04-02T09:00:00Z"
}
```

## Key properties
- **No auth required** — anonymous public access.
- **No named data** — procuring_entity, supplier, anchored_by are never in the response.
- **Document discarded** — bytes are read, hashed, then dropped. Nothing stored.
- **Rate limited** — 120 req/min per IP (slowapi).
- **Input validated** — non-PDF → 415, empty file → 400, file > 20 MB → 413.

## Acceptance criteria — results
| Criterion | Test | Result |
|-----------|------|:------:|
| Original → MATCH | `test_public_verify_match` | ✅ |
| Modified byte → MISMATCH | `test_public_verify_mismatch` | ✅ |
| Unknown OCID → NOT_REGISTERED | `test_public_verify_unknown_ocid` | ✅ |
| No auth needed | `test_public_verify_requires_no_auth` | ✅ |
| No named data in response | `test_public_verify_response_contains_no_named_data` | ✅ |
| Single byte tamper caught | `test_public_verify_single_byte_tamper_detected` | ✅ |
| Non-PDF rejected 415 | `test_public_verify_rejects_non_pdf` | ✅ |
| Empty file rejected 400 | `test_public_verify_rejects_empty_file` | ✅ |

## Tests — 243/243 green (11 new)

## Progress update
- INC-007 = **DONE** — Overall: **40%** (3+5+6+6+6+4+6+4).
