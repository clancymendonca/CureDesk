from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.auth.firebase import verify_token_required
from app.db.models import PrescriptionScan, SymptomSubmission, get_db
from app.schemas import HistoryItem, ProfileHistoryResponse

router = APIRouter(prefix="/v1/profile", tags=["profile"])


@router.get("/history", response_model=ProfileHistoryResponse)
def profile_history(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    user = verify_token_required(db, authorization)

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
                id=f"symptom:{s.id}",
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
        text = p.ocr_text[:60] + ("..." if len(p.ocr_text) > 60 else "")
        items.append(
            HistoryItem(
                id=f"prescription:{p.id}",
                type="prescription",
                created_at=p.created_at.isoformat(),
                summary=f"Prescription scan — {text}",
            )
        )

    items.sort(key=lambda x: x.created_at, reverse=True)
    return ProfileHistoryResponse(items=items[:30])
