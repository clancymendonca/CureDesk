"""Chat context: crisis detection and DB-grounded RAG."""

from __future__ import annotations

import re
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Disease, Drug, KnowledgeChunk

CRISIS_PATTERNS = [
    r"\bchest pain\b",
    r"\bcan'?t breathe\b",
    r"\bcan not breathe\b",
    r"\bstroke\b",
    r"\bsuicid",
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bsevere bleeding\b",
    r"\bunconscious\b",
    r"\bheart attack\b",
    r"\banaphyla",
]

CRISIS_REPLY = (
    "If you are experiencing a medical emergency — including chest pain, difficulty "
    "breathing, signs of stroke, severe bleeding, or thoughts of self-harm — please "
    "call emergency services (911 in the US) or go to the nearest emergency department "
    "immediately. CureDesk cannot provide emergency care."
)


def is_crisis_message(message: str) -> bool:
    lower = message.lower()
    return any(re.search(p, lower) for p in CRISIS_PATTERNS)


def _extract_terms(message: str) -> list[str]:
    words = re.findall(r"[a-zA-Z]{3,}", message.lower())
    stop = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
        "her", "was", "one", "our", "out", "day", "get", "has", "him", "his",
        "how", "its", "may", "new", "now", "old", "see", "way", "who", "did",
        "what", "when", "where", "which", "with", "have", "this", "that",
        "from", "they", "been", "than", "into", "just", "like", "over", "such",
        "take", "your", "about", "would", "there", "their", "will", "each",
    }
    return [w for w in words if w not in stop][:12]


def _search_knowledge_chunks(db: Session, terms: list[str]) -> list[KnowledgeChunk]:
    hits: list[KnowledgeChunk] = []
    for term in terms:
        for chunk in (
            db.query(KnowledgeChunk)
            .filter(
                KnowledgeChunk.question.ilike(f"%{term}%")
                | KnowledgeChunk.answer.ilike(f"%{term}%")
            )
            .limit(3)
        ):
            if chunk not in hits:
                hits.append(chunk)
        if len(hits) >= 5:
            break
    return hits[:5]


def build_db_context(db: Session, message: str) -> str:
    terms = _extract_terms(message)
    if not terms:
        return ""

    disease_hits: list[Disease] = []
    drug_hits: list[Drug] = []
    qa_hits = _search_knowledge_chunks(db, terms)

    for term in terms:
        for d in db.query(Disease).filter(Disease.name.ilike(f"%{term}%")).limit(3):
            if d not in disease_hits:
                disease_hits.append(d)
        for d in db.query(Drug).filter(
            (Drug.brand_name.ilike(f"%{term}%")) | (Drug.generic_name.ilike(f"%{term}%"))
        ).limit(3):
            if d not in drug_hits:
                drug_hits.append(d)

    if not disease_hits and not drug_hits and not qa_hits:
        return ""

    lines = ["Relevant information from the CureDesk knowledge base (use only this for factual claims):"]
    for d in disease_hits[:5]:
        symptoms = d.common_symptoms or {}
        sym_str = ", ".join(f"{k}: {v}" for k, v in list(symptoms.items())[:4])
        lines.append(f"- Disease: {d.name}. {d.description or ''} Common symptom rates: {sym_str or 'n/a'}.")
    for d in drug_hits[:5]:
        lines.append(f"- Drug: brand {d.brand_name}, generic {d.generic_name}.")
    for chunk in qa_hits:
        answer = chunk.answer.replace("\n", " ").strip()
        if len(answer) > 400:
            answer = answer[:400] + "..."
        lines.append(f"- Q: {chunk.question} A: {answer}")
    lines.append("If the user asks about something not listed above, say you are not sure and recommend a clinician.")
    return "\n".join(lines)


def build_system_prompt(db: Session, message: str, base_prompt: str) -> str:
    ctx = build_db_context(db, message)
    if ctx:
        return f"{base_prompt}\n\n{ctx}"
    return base_prompt
