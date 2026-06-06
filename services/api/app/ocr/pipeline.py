import sys

from pathlib import Path

from typing import Optional



from sqlalchemy.orm import Session



from app.config import settings

from app.db.models import Drug



_REPO_ROOT = Path(__file__).resolve().parents[4]

if str(_REPO_ROOT) not in sys.path:

    sys.path.insert(0, str(_REPO_ROOT))



from ml.ocr.pipeline_core import extract_text_with_engine, lookup_drugs_from_db



_easyocr_reader = None

_paddle_reader = None





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





def lookup_drugs(db: Session, ocr_text: str, limit: int = 5) -> list[dict]:

    drugs = db.query(Drug).all()

    if not drugs:

        return []

    drug_list = [(d.brand_name, d.generic_name) for d in drugs]

    return lookup_drugs_from_db(ocr_text, drug_list, limit=limit)


