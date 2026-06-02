"""Celery tasks for anomaly analysis + risk scoring (INC-005 hardening)."""
import asyncio
import logging

from app.tasks.celery_app import celery_app

log = logging.getLogger(__name__)


@celery_app.task(bind=True, name="analysis.score_contract", max_retries=2, default_retry_delay=30)
def score_contract_task(self, ocid: str):
    """Score a single contract asynchronously."""
    async def _run():
        from app.db.session import AsyncSessionLocal
        from app.services.scoring_service import score_contract
        async with AsyncSessionLocal() as db:
            result = await score_contract(db, ocid)
            log.info("Scored %s — score=%d tier=%s", ocid, result["score"], result["tier"])

    try:
        asyncio.run(_run())
    except Exception as exc:
        log.error("Failed to score %s: %s", ocid, exc)
        raise self.retry(exc=exc)


@celery_app.task(bind=True, name="analysis.score_all", max_retries=1)
def score_all_task(self, ocids: list[str] | None = None):
    """Score all contracts (or a subset). Dispatches individual tasks per contract."""
    async def _get_ocids():
        if ocids:
            return ocids
        from app.db.session import AsyncSessionLocal
        from app.models.contract import Contract
        from sqlalchemy import select
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Contract.ocid))
            return [row[0] for row in result.all()]

    all_ocids = asyncio.run(_get_ocids())
    log.info("Dispatching scoring tasks for %d contracts", len(all_ocids))
    for ocid in all_ocids:
        score_contract_task.delay(ocid)
