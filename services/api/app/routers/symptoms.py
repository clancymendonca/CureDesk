from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.firebase import verify_token_optional
from app.db.models import SymptomSubmission, get_db
from app.limiter import limiter
from app.ml import symptoms as ml
from app.schemas import SymptomFeaturesResponse, SymptomPredictResponse, SymptomRequest

router = APIRouter(prefix="/v1/symptoms", tags=["symptoms"])


@router.get("/features", response_model=SymptomFeaturesResponse)
async def list_symptom_features():
    if not ml.is_ready():
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "ML_NOT_READY", "message": "Model not loaded"}},
        )
    features = ml.get_symptom_features()
    if not features:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NO_FEATURES", "message": "Wide feature list not available"}},
        )
    return SymptomFeaturesResponse(
        features=features,
        model_version=ml.get_model_version(),
        feature_format=ml.get_feature_format(),
    )


@router.post("/predict", response_model=SymptomPredictResponse)
@limiter.limit("60/hour")
async def predict_symptoms(
    request: Request,
    body: SymptomRequest,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(default=None),
):
    if not ml.is_ready():
        raise HTTPException(
            status_code=503,
            detail={"error": {"code": "ML_NOT_READY", "message": "Model not loaded"}},
        )

    data = body.model_dump()
    predictions, confidence_level = ml.predict_top_k(data, k=3)
    version = ml.get_model_version()
    user = verify_token_optional(db, authorization)

    submission = SymptomSubmission(
        user_id=user.id if user else None,
        inputs=data,
        predictions={"items": predictions, "confidence_level": confidence_level},
        model_version=version,
    )
    db.add(submission)
    db.commit()

    return SymptomPredictResponse(
        predictions=predictions,
        model_version=version,
        confidence_level=confidence_level,
    )
