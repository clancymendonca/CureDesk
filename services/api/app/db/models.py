from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _utcnow() -> datetime:
    """Timezone-aware replacement for the deprecated datetime.utcnow."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    photo_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    symptom_submissions: Mapped[list["SymptomSubmission"]] = relationship(back_populates="user")
    prescription_scans: Mapped[list["PrescriptionScan"]] = relationship(back_populates="user")


class Disease(Base):
    __tablename__ = "diseases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)
    common_symptoms: Mapped[Optional[dict]] = mapped_column(JSON)

    patient_profiles: Mapped[list["PatientProfile"]] = relationship(back_populates="disease")


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    disease_id: Mapped[int] = mapped_column(ForeignKey("diseases.id"))
    fever: Mapped[bool] = mapped_column(default=False)
    cough: Mapped[bool] = mapped_column(default=False)
    fatigue: Mapped[bool] = mapped_column(default=False)
    difficulty_breathing: Mapped[bool] = mapped_column(default=False)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(16))
    blood_pressure: Mapped[str] = mapped_column(String(16))
    cholesterol_level: Mapped[str] = mapped_column(String(16))

    disease: Mapped["Disease"] = relationship(back_populates="patient_profiles")


class Drug(Base):
    __tablename__ = "drugs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand_name: Mapped[str] = mapped_column(String(255), index=True)
    generic_name: Mapped[str] = mapped_column(String(255), index=True)


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(64), index=True)
    question: Mapped[str] = mapped_column(Text, index=True)
    answer: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Optional[bytes]] = mapped_column(LargeBinary)
    embedding_model: Mapped[Optional[str]] = mapped_column(String(128))


class SymptomSubmission(Base):
    __tablename__ = "symptom_submissions"
    __table_args__ = (
        Index("ix_symptom_submissions_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    inputs: Mapped[dict] = mapped_column(JSON)
    predictions: Mapped[dict] = mapped_column(JSON)
    model_version: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    user: Mapped[Optional["User"]] = relationship(back_populates="symptom_submissions")


class PrescriptionScan(Base):
    __tablename__ = "prescription_scans"
    __table_args__ = (
        Index("ix_prescription_scans_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    ocr_text: Mapped[str] = mapped_column(Text)
    matched_drug_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drugs.id"))
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    user: Mapped[Optional["User"]] = relationship(back_populates="prescription_scans")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
