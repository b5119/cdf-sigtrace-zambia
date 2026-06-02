"""Celery tasks for OCDS ingestion (INC-005 hardening)."""
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app

log = logging.getLogger(__name__)


@celery_app.task(bind=True, name="ingestion.run", max_retries=3, default_retry_delay=60)
def run_ingestion(self, run_id: str, source: str, since: str | None = None):
    """
    Execute a full OCDS ingestion run asynchronously.
    The run record is pre-created by the API; this task fills in the results.
    """
    async def _run():
        from app.db.session import AsyncSessionLocal
        from app.models.contract import IngestionRun
        from ingestion.fetch import fetch_from_api, load_sample
        from ingestion.normalise import normalise_records
        from ingestion.load import run_load
        from sqlalchemy import select

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(IngestionRun).where(IngestionRun.id == run_id))
            run = result.scalar_one_or_none()
            if not run:
                log.error("IngestionRun %s not found", run_id)
                return

            try:
                if source == "sample":
                    raw = load_sample()
                else:
                    raw = fetch_from_api(since=since)

                run.records_in = len(raw)
                normalised = normalise_records(raw)
                await run_load(db, normalised, run)
                log.info("Ingestion run %s complete — %d loaded", run_id, run.records_loaded)
            except Exception as exc:
                log.error("Ingestion run %s failed: %s", run_id, exc)
                run.status = "failed"
                run.finished_at = datetime.now(timezone.utc)
                run.errors = [{"error": str(exc)}]
                await db.commit()
                raise self.retry(exc=exc)

    asyncio.run(_run())
