# ingestion — OCDS pipeline

Fetches OCDS records/record-packages, normalises them, and loads Contract/Supplier/Tender into the
DB. Idempotent on OCID + content hash so re-runs don't duplicate. Built in **INC-002**.

```
ingestion/
  fetch.py     pull OCDS records (and the published analytics where useful)
  normalise.py map OCDS → domain models (handle framework_parent, dates, documents)
  load.py      upsert into DB; record an IngestionRun with counts + errors
  run.py       python -m ingestion.run [--sample] [--since DATE]
tests/         uses the OCDS sample fixture from docs/10_TESTING.md
```
Exposed via backend `/ingestion/runs` (admin) and scheduled as a Celery task.
