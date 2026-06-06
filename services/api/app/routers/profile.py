from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.auth.firebase import verify_token_optional
from app.db.models import PrescriptionScan, SymptomSubmission, get_db
from app.schemas import HistoryItem, ProfileHistoryResponse

router = APIRouter(prefix="/v1/profile", tags=["profile"])


@router.get("/history", response_model=ProfileHistoryResponse)
def profile_history(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    user = verify_token_optional(db, authorization)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Sign in required"}},
        )

    items: list[HistoryItem] = []

    for s in (
        db.query(SymptomSubmission)
        .filter(SymptomSubmission.user_id == user.id)
        .order_by(SymptomSubmission.created_at.desc())
        .limit(20)
        .all()
    ):
        preds = s.predictions.get("items", [])
        top = preds[0]["disease"] if preds else "Unknown"
        items.append(
            HistoryItem(
                id=s.id,
                type="symptom",
                created_at=s.created_at.isoformat(),
                summary=f"Symptom check — top: {top}",
            )
        )

    for p in (
        db.query(PrescriptionScan)
        .filter(PrescriptionScan.user_id == user.id)
        .order_by(PrescriptionScan.created_at.desc())
        .limit(20)
        .all()
    ):
        items.append(
            HistoryItem(
                id=p.id,
                type="prescription",
                created_at=p.created_at.isoformat(),
                summary=f"Prescription scan — {p.ocr_text[:60]}...",
            )
        )

    items.sort(key=lambda x: x.created_at, reverse=True)
    return ProfileHistoryResponse(items=items[:30])
