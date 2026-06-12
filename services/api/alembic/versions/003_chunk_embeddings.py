"""003 embedding column on knowledge chunks for semantic RAG

Revision ID: 003_chunk_embeddings
Revises: 002_knowledge_chunks
Create Date: 2026-06-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003_chunk_embeddings"
down_revision: Union[str, None] = "002_knowledge_chunks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("knowledge_chunks", sa.Column("embedding", sa.LargeBinary(), nullable=True))
    op.add_column(
        "knowledge_chunks", sa.Column("embedding_model", sa.String(length=128), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("knowledge_chunks", "embedding_model")
    op.drop_column("knowledge_chunks", "embedding")
