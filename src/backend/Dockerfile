FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt "pydantic[email]" aiosqlite

COPY . .
# Default to SQLite + mock ledgers so it runs anywhere for free.
# Override DATABASE_URL / *_MOCK_MODE via env for production.
ENV DATABASE_URL=sqlite+aiosqlite:///./cdf.db \
    MFA_ENFORCE=false \
    FABRIC_MOCK_MODE=true POLYGON_MOCK_MODE=true IPFS_MOCK_MODE=true

EXPOSE 8000
# Seed on first boot if the db doesn't exist, then serve
CMD ["sh", "-c", "python scripts/local_seed.py 2>/dev/null || true; uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
