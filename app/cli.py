import os

import uvicorn
from dotenv import load_dotenv

from app.core.logging import getLogger

load_dotenv(".env")

logger = getLogger(__name__)


def main():
    host = os.environ.get("HOST", None)
    port = os.environ.get("PORT", None)
    reload = os.environ.get("RELOAD_SERVER", False)
    worker_count = os.environ.get("WORKER_COUNT", None)

    if host is None or port is None:
        logger.error(
            f"Host or port is not configured in the environment: host='{host}', port='{port}'"
        )
        exit(1)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=int(port),
        reload=bool(reload),
        workers=int(worker_count) if worker_count else None,
    )
