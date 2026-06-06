from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.models import Disease, get_db
from app.schemas import DiseaseListResponse, DiseaseSummary

router = APIRouter(prefix="/v1/diseases", tags=["diseases"])


@router.get("", response_model=DiseaseListResponse)
def list_diseases(
    q: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Disease)
    if q:
        query = query.filter(Disease.name.ilike(f"%{q}%"))
    total = query.count()
    items = query.order_by(Disease.name).limit(50).all()
    return DiseaseListResponse(items=items, total=total)


@router.get("/{slug}", response_model=DiseaseSummary)
def get_disease(slug: str, db: Session = Depends(get_db)):
    disease = db.query(Disease).filter(Disease.slug == slug).first()
    if not disease:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_FOUND", "message": "Disease not found"}},
        )
    return disease
