"""Run Alembic migrations programmatically."""

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    api_root = Path(__file__).resolve().parents[2]
    cfg = Config(str(api_root / "alembic.ini"))
    try:
        command.upgrade(cfg, "head")
    except Exception:
        # Starting with a stale/missing schema leads to confusing runtime
        # failures, so fail fast instead of limping along.
        logger.exception("Alembic migration failed; refusing to start with a stale schema")
        raise
