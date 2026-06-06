import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, File, Header, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.auth.firebase import verify_token_optional
from app.config import settings
from app.db.models import Drug, PrescriptionScan, get_db
from app.limiter import limiter
from app.ocr.pipeline import extract_text, lookup_drugs
from app.schemas import PrescriptionScanResponse

router = APIRouter(prefix="/v1/prescriptions", tags=["prescriptions"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg"}


@router.post("/scan", response_model=PrescriptionScanResponse)
@limiter.limit("10/hour")
async def scan_prescription(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_FILE",
                    "message": "Only JPEG and PNG images are allowed",
                }
            },
        )

    data = await file.read()
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
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "OCR_FAILED",
                    "message": f"Could not process image: {e}",
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
