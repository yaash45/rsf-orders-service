import uvicorn

from app.core.config import Environments, config
from app.core.logging import getLogger

logger = getLogger(__name__)


def main():
    host = config.HOST
    port = config.PORT
    reload = config.ENVIRONMENT == Environments.DEV

    if host is None or port is None:
        logger.error(
            f"Host or port is not configured in the environment: host='{host}', port='{port}'"
        )
        exit(1)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=bool(reload),
    )
