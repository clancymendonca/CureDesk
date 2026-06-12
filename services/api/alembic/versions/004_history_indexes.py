"""004 indexes for profile history queries

Revision ID: 004_history_indexes
Revises: 003_chunk_embeddings
Create Date: 2026-06-12
"""

from typing import Sequence, Union

from alembic import op

revision: str = "004_history_indexes"
down_revision: Union[str, None] = "003_chunk_embeddings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_symptom_submissions_user_created",
        "symptom_submissions",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_prescription_scans_user_created",
        "prescription_scans",
        ["user_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_prescription_scans_user_created", table_name="prescription_scans")
    op.drop_index("ix_symptom_submissions_user_created", table_name="symptom_submissions")
