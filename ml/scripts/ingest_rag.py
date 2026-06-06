"""Load MedQuad + lavita CSVs into Postgres for chat RAG."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api"))

from app.db.models import KnowledgeChunk, SessionLocal

MEDQUAD = ROOT / "ml" / "data" / "rag" / "medquad" / "train.csv"
LAVITA_DIR = ROOT / "ml" / "data" / "rag" / "medical_qa_lavita"
LAVITA_FILES = [
    "medical_meadow_wikidoc.csv",
    "medical_meadow_health_advice.csv",
]


def _ingest_csv(
    db,
    path: Path,
    *,
    source: str,
    question_col: str,
    answer_col: str,
    limit: int = 0,
) -> int:
    if not path.exists():
        print(f"Skip missing {path}")
        return 0
    added = 0
    with path.open(newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            if limit and i >= limit:
                break
            q = (row.get(question_col) or "").strip()
            a = (row.get(answer_col) or "").strip()
            if not q or not a:
                continue
            if len(a) > 8000:
                a = a[:8000] + "..."
            exists = (
                db.query(KnowledgeChunk)
                .filter(KnowledgeChunk.source == source, KnowledgeChunk.question == q)
                .first()
            )
            if exists:
                continue
            db.add(KnowledgeChunk(source=source, question=q, answer=a))
            added += 1
            if added % 500 == 0:
                db.commit()
    db.commit()
    return added


def main() -> None:
    from app.db.migrate import run_migrations

    run_migrations()
    db = SessionLocal()
    try:
        n = _ingest_csv(db, MEDQUAD, source="medquad", question_col="Question", answer_col="Answer")
        print(f"Ingested {n} MedQuad chunks")
        total = n
        for name in LAVITA_FILES:
            path = LAVITA_DIR / name
            added = _ingest_csv(
                db,
                path,
                source=f"lavita:{name}",
                question_col="instruction",
                answer_col="output",
                limit=3000,
            )
            print(f"Ingested {added} from {name}")
            total += added
        print(f"Total new knowledge chunks: {total}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
