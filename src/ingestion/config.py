"""Ingestion pipeline settings."""
import os

# ZPPA/e-GP OCDS publication endpoint (set via env)
OCDS_API_URL: str = os.getenv(
    "OCDS_API_URL",
    "https://ocds.zppa.org.zm/api/ocds/records",
)
OCDS_API_KEY: str = os.getenv("OCDS_API_KEY", "")
OCDS_BATCH_SIZE: int = int(os.getenv("OCDS_BATCH_SIZE", "100"))

SAMPLE_FILE: str = os.path.join(os.path.dirname(__file__), "sample", "ocds_sample.json")
