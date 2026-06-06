from typing import Literal, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


class SymptomRequest(BaseModel):
    fever: bool
    cough: bool
    fatigue: bool
    difficulty_breathing: bool
    age: int = Field(ge=0, le=120)
    gender: Literal["male", "female"]
    blood_pressure: Literal["normal", "high", "low"]
    cholesterol_level: Literal["normal", "high"]
    symptoms: Optional[dict[str, bool]] = Field(
        default=None,
        description="Extended wide-model symptom flags (132 features)",
    )


class SymptomFeaturesResponse(BaseModel):
    features: list[str]
    model_version: str
    feature_format: str


class DiseasePrediction(BaseModel):
    disease: str
    slug: str
    probability: float


class SymptomPredictResponse(BaseModel):
    predictions: list[DiseasePrediction]
    model_version: str
    confidence_level: Literal["high", "medium", "low"]


class DiseaseSummary(BaseModel):
    id: int
    slug: str
    name: str
    description: Optional[str] = None
    common_symptoms: Optional[dict] = None

    model_config = {"from_attributes": True}


class DiseaseListResponse(BaseModel):
    items: list[DiseaseSummary]
    total: int


class DrugMatch(BaseModel):
    brand: str
    generic: str
    confidence: float


class PrescriptionScanResponse(BaseModel):
    ocr_text: str
    matches: list[DrugMatch]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str


class HistoryItem(BaseModel):
    id: int
    type: Literal["symptom", "prescription"]
    created_at: str
    summary: str


class ProfileHistoryResponse(BaseModel):
    items: list[HistoryItem]
