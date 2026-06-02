# anomaly-engine — the 8 integrity checks

Importable Python library + CLI that runs the eight checks over normalised contract records and
produces per-contract flags + a weighted 0–100 risk score. Used by the backend (`analysis/run`) and
runnable standalone. Spec: `../../docs/00_PROJECT_OVERVIEW.md`, weights/thresholds via Config.

Checks (INC-003 = 1–3, INC-004 = 4–8):
1. Signing completeness · 2. Standstill compliance (<14d) · 3. Stage time-gap (identical timestamps)
4. Document forensics (PDF metadata vs signing date) · 5. Supplier network (shared attributes)
6. Score variance (near-zero across evaluators) · 7. Amendment value (>15%) · 8. Debarment cross-ref.

Intended structure:
```
engine/
  checks/            one module per check, each: def run(contract, ctx) -> Flag | None
  scoring.py         weighted sum → normalised 0–100 (weights from config)
  safeguards.py      framework-call-off exclusion; lawful-emergency handling
  cli.py             python -m engine.cli --ocid <ocid> | --range <dates>
tests/               positive + negative fixtures per check (see docs/10_TESTING.md)
```
Design rule: each check is an explicit, reproducible computation — **no opaque ML**.
