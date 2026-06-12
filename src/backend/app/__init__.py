"""CDF SigTrace backend package.

Make the standalone anomaly engine (src/anomaly-engine) importable at runtime.
Tests get this via pytest.ini's pythonpath, but uvicorn / scripts / Celery do
not — so add it here, which runs on the first `import app.*`.
"""
import os
import sys

_ENGINE_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "anomaly-engine")
)
if os.path.isdir(_ENGINE_DIR) and _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)
