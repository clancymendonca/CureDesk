import logging
import sys
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Drug

def _find_ml_root() -> Optional[Path]:
    """Locate the directory containing the ``ml`` package.

    Works both when running from the monorepo (ml/ at repo root, four levels
    up) and inside Docker (ml/ copied/mounted next to the app, e.g. /app/ml).
    """
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "ml" / "ocr" / "pipeline_core.py").exists():
            return candidate
    return None


_ML_ROOT = _find_ml_root()
if _ML_ROOT is None:
    raise ImportError(
        "Could not locate the 'ml' package (ml/ocr/pipeline_core.py). "
        "Ensure the ml/ directory is present next to the API app "
        "(repo root in development, /app/ml in Docker)."
    )
if str(_ML_ROOT) not in sys.path:
    sys.path.insert(0, str(_ML_ROOT))

from ml.ocr.pipeline_core import extract_text_with_engine, lookup_drugs_from_db

logger = logging.getLogger(__name__)

_easyocr_reader = None
_paddle_reader = None

# (row count, [(brand, generic), ...]) — refreshed when the drugs table changes size.
_drug_cache: Optional[tuple[int, list[tuple[str, str]]]] = None


def _get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr

        _easyocr_reader = easyocr.Reader(["en"], gpu=settings.ocr_gpu_enabled)
    return _easyocr_reader


def _get_paddle_reader():
    global _paddle_reader
    if _paddle_reader is None:
        from paddleocr import PaddleOCR

        _paddle_reader = PaddleOCR(
            use_angle_cls=True,
            lang="en",
            use_gpu=settings.ocr_gpu_enabled,
            show_log=False,
        )
    return _paddle_reader


def warm_up() -> None:
    """Pre-load the configured OCR reader so the first scan doesn't time out."""
    engine = settings.ocr_engine.strip().lower()
    if engine in ("easyocr", "ensemble"):
        _get_easyocr_reader()
        logger.info("EasyOCR reader warmed up")
    if engine in ("paddle", "ensemble"):
        try:
            _get_paddle_reader()
            logger.info("PaddleOCR reader warmed up")
        except ImportError:
            logger.warning("PaddleOCR not installed, skipping warm-up")


def extract_text(image_bytes: bytes) -> str:
    engine = settings.ocr_engine.strip().lower()
    easy = _get_easyocr_reader() if engine in ("easyocr", "ensemble") else None
    paddle = None
    if engine in ("paddle", "ensemble"):
        try:
            paddle = _get_paddle_reader()
        except ImportError:
            if engine == "paddle":
                raise RuntimeError(
                    "PaddleOCR not installed. pip install paddleocr or set OCR_ENGINE=easyocr"
                )
    return extract_text_with_engine(
        image_bytes,
        engine=engine,
        use_gpu=settings.ocr_gpu_enabled,
        easyocr_reader=easy,
        paddle_reader=paddle,
    )


def _get_drug_list(db: Session) -> list[tuple[str, str]]:
    global _drug_cache
    count = db.query(Drug).count()
    if _drug_cache is not None and _drug_cache[0] == count:
        return _drug_cache[1]
    rows = db.query(Drug.brand_name, Drug.generic_name).all()
    drug_list = [(brand, generic) for brand, generic in rows]
    _drug_cache = (count, drug_list)
    return drug_list


def lookup_drugs(db: Session, ocr_text: str, limit: int = 5) -> list[dict]:
    drug_list = _get_drug_list(db)
    if not drug_list:
        return []
    return lookup_drugs_from_db(ocr_text, drug_list, limit=limit)
