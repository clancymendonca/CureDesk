"""Optional sentence-transformer embeddings for semantic RAG retrieval.

Everything here degrades gracefully: if sentence-transformers is not
installed, the model can't be loaded, or no chunk embeddings exist in the
DB, callers fall back to keyword search.
"""

from __future__ import annotations

import logging
import threading
from typing import Optional

import numpy as np
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import KnowledgeChunk

logger = logging.getLogger(__name__)

# Minimum cosine similarity for a chunk to count as relevant context.
MIN_SIMILARITY = 0.35

_model = None
_model_failed = False
_model_lock = threading.Lock()

_index_lock = threading.Lock()
_index_ids: list[int] = []
_index_matrix: Optional[np.ndarray] = None
_index_loaded = False


def get_embedding_model():
    """Lazy-load the sentence-transformer model. Returns None if unavailable."""
    global _model, _model_failed
    if _model is not None or _model_failed:
        return _model
    with _model_lock:
        if _model is not None or _model_failed:
            return _model
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer(settings.embedding_model)
        except Exception as exc:
            logger.warning(
                "Embedding model unavailable, chat falls back to keyword RAG: %s", exc
            )
            _model_failed = True
    return _model


def embed_texts(texts: list[str]) -> Optional[np.ndarray]:
    model = get_embedding_model()
    if model is None:
        return None
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vecs, dtype=np.float32)


def vector_to_bytes(vec: np.ndarray) -> bytes:
    return np.asarray(vec, dtype=np.float32).tobytes()


def bytes_to_vector(raw: bytes) -> np.ndarray:
    return np.frombuffer(raw, dtype=np.float32)


def load_index(db: Session, *, force: bool = False) -> bool:
    """Load all chunk embeddings into an in-memory matrix for cosine search."""
    global _index_ids, _index_matrix, _index_loaded
    if _index_loaded and not force:
        return _index_matrix is not None
    with _index_lock:
        if _index_loaded and not force:
            return _index_matrix is not None
        try:
            rows = (
                db.query(KnowledgeChunk.id, KnowledgeChunk.embedding)
                .filter(KnowledgeChunk.embedding.isnot(None))
                .all()
            )
        except Exception as exc:
            logger.warning("Could not load chunk embeddings: %s", exc)
            rows = []
        ids: list[int] = []
        vectors: list[np.ndarray] = []
        dim: Optional[int] = None
        for chunk_id, raw in rows:
            vec = bytes_to_vector(raw)
            if dim is None:
                dim = vec.shape[0]
            if vec.shape[0] != dim:
                continue
            ids.append(chunk_id)
            vectors.append(vec)
        _index_ids = ids
        _index_matrix = np.vstack(vectors) if vectors else None
        _index_loaded = True
        if _index_matrix is not None:
            logger.info("Loaded %d chunk embeddings for semantic RAG", len(ids))
    return _index_matrix is not None


def reset_index() -> None:
    global _index_ids, _index_matrix, _index_loaded
    with _index_lock:
        _index_ids = []
        _index_matrix = None
        _index_loaded = False


def search_chunks(db: Session, message: str, k: int = 5) -> list[KnowledgeChunk]:
    """Return top-k semantically similar chunks, or [] if semantic search is unavailable."""
    if not load_index(db):
        return []
    query_vec = embed_texts([message])
    if query_vec is None or _index_matrix is None:
        return []
    sims = _index_matrix @ query_vec[0]
    top = np.argsort(sims)[::-1][:k]
    ordered_ids = [_index_ids[i] for i in top if float(sims[i]) >= MIN_SIMILARITY]
    if not ordered_ids:
        return []
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.id.in_(ordered_ids)).all()
    by_id = {c.id: c for c in chunks}
    return [by_id[i] for i in ordered_ids if i in by_id]
