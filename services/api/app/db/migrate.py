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
    except Exception as exc:
        logger.warning("Alembic migration skipped: %s", exc)
