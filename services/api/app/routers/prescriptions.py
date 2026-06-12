import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Header, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.auth.firebase import verify_token_optional
from app.config import settings
from app.db.models import Drug, PrescriptionScan, get_db
from app.limiter import limiter
from app.ocr.pipeline import extract_text, lookup_drugs
from app.schemas import PrescriptionScanResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/prescriptions", tags=["prescriptions"])

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _is_supported_image(data: bytes) -> bool:
    """Validate by magic bytes; client Content-Type headers can't be trusted
    (React Native blobs often arrive as application/octet-stream)."""
    return data.startswith(JPEG_MAGIC) or data.startswith(PNG_MAGIC)


@router.post("/scan", response_model=PrescriptionScanResponse)
@limiter.limit("10/hour")
async def scan_prescription(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    data = await file.read()
    if not _is_supported_image(data):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_FILE",
                    "message": "Only JPEG and PNG images are allowed",
                }
            },
        )

    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": "Image must be under 5MB",
                }
            },
        )

    user = verify_token_optional(db, authorization)

    try:
        ocr_text = await asyncio.wait_for(
            asyncio.to_thread(extract_text, data),
            timeout=settings.ocr_timeout_seconds,
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail={
                "error": {
                    "code": "OCR_TIMEOUT",
                    "message": "OCR took too long. Please try a clearer image.",
                }
            },
        )
    except Exception:
        # Log full details server-side; don't leak internals to clients.
        logger.exception("OCR processing failed")
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "OCR_FAILED",
                    "message": "Could not process image. Please try a clearer photo.",
                }
            },
        )

    matches = lookup_drugs(db, ocr_text)
    top = matches[0] if matches else None
    drug_id = None
    confidence = None
    if top:
        drug = db.query(Drug).filter(Drug.brand_name == top["brand"]).first()
        if drug:
            drug_id = drug.id
            confidence = top["confidence"]

    scan = PrescriptionScan(
        user_id=user.id if user else None,
        ocr_text=ocr_text,
        matched_drug_id=drug_id,
        confidence=confidence,
    )
    db.add(scan)
    db.commit()

    return PrescriptionScanResponse(ocr_text=ocr_text, matches=matches)
