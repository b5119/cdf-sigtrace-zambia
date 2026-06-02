"""Fetch OCDS records from a remote endpoint or local sample file."""
import json
import logging
from typing import Iterator

import httpx

from ingestion.config import OCDS_API_KEY, OCDS_API_URL, OCDS_BATCH_SIZE, SAMPLE_FILE

log = logging.getLogger(__name__)


def _iter_records_from_package(package: dict) -> Iterator[dict]:
    """Yield individual records from an OCDS record-package."""
    for record in package.get("records", []):
        yield record


def load_sample() -> list[dict]:
    """Load the bundled OCDS sample fixture from disk."""
    with open(SAMPLE_FILE, "r", encoding="utf-8") as f:
        package = json.load(f)
    records = list(_iter_records_from_package(package))
    log.info("Loaded %d records from sample file", len(records))
    return records


def fetch_from_api(since: str | None = None, max_pages: int = 100) -> list[dict]:
    """
    Fetch OCDS records from the configured API endpoint.
    Handles pagination via `next` link in the record-package.
    """
    headers = {}
    if OCDS_API_KEY:
        headers["Authorization"] = f"Bearer {OCDS_API_KEY}"

    records: list[dict] = []
    url = OCDS_API_URL
    params: dict = {"pageSize": OCDS_BATCH_SIZE}
    if since:
        params["since"] = since

    page = 0
    with httpx.Client(timeout=30) as client:
        while url and page < max_pages:
            log.info("Fetching OCDS page %d from %s", page + 1, url)
            try:
                resp = client.get(url, headers=headers, params=params if page == 0 else {})
                resp.raise_for_status()
                package = resp.json()
                page_records = list(_iter_records_from_package(package))
                records.extend(page_records)
                log.info("Page %d: %d records", page + 1, len(page_records))
                # Follow pagination link if present
                links = package.get("links", {})
                url = links.get("next")
                params = {}
                page += 1
            except httpx.HTTPStatusError as e:
                log.error("HTTP error fetching OCDS: %s", e)
                break
            except Exception as e:
                log.error("Error fetching OCDS: %s", e)
                break

    log.info("Total OCDS records fetched: %d", len(records))
    return records
