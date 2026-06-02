"""CLI entry point: python -m ingestion.run [--sample] [--since DATE] [--url URL]"""
import argparse
import asyncio
import logging
import sys
import uuid
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


async def _run(args: argparse.Namespace) -> None:
    # Import here so the CLI can run without the full FastAPI app being loaded
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from app.db.session import AsyncSessionLocal
    from app.models.contract import IngestionRun
    from ingestion.fetch import fetch_from_api, load_sample
    from ingestion.normalise import normalise_records
    from ingestion.load import run_load

    async with AsyncSessionLocal() as db:
        source = "sample" if args.sample else (args.url or "api")
        run = IngestionRun(id=uuid.uuid4(), source=source, status="running")
        db.add(run)
        await db.flush()

        if args.sample:
            log.info("Loading from sample file")
            raw_records = load_sample()
        else:
            log.info("Fetching from API%s", f" (since {args.since})" if args.since else "")
            raw_records = fetch_from_api(since=args.since)

        run.records_in = len(raw_records)
        normalised = normalise_records(raw_records)

        await run_load(db, normalised, run)
        log.info(
            "Run %s finished — status=%s loaded=%d updated=%d skipped=%d errors=%d",
            run.id, run.status, run.records_loaded, run.records_updated,
            run.records_skipped, len(run.errors),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="CDF SigTrace OCDS ingestion pipeline")
    parser.add_argument("--sample", action="store_true", help="Load from bundled OCDS sample file")
    parser.add_argument("--since", default=None, help="Fetch only records updated since DATE (ISO)")
    parser.add_argument("--url", default=None, help="Override the OCDS API URL for this run")
    args = parser.parse_args()

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
