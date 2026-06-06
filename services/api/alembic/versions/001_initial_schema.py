"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-06-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("firebase_uid", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("photo_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_firebase_uid"), "users", ["firebase_uid"], unique=True)

    op.create_table(
        "diseases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("common_symptoms", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_diseases_slug"), "diseases", ["slug"], unique=True)

    op.create_table(
        "drugs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("brand_name", sa.String(length=255), nullable=False),
        sa.Column("generic_name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_drugs_brand_name"), "drugs", ["brand_name"], unique=False)
    op.create_index(op.f("ix_drugs_generic_name"), "drugs", ["generic_name"], unique=False)

    op.create_table(
        "patient_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("disease_id", sa.Integer(), nullable=False),
        sa.Column("fever", sa.Boolean(), nullable=False),
        sa.Column("cough", sa.Boolean(), nullable=False),
        sa.Column("fatigue", sa.Boolean(), nullable=False),
        sa.Column("difficulty_breathing", sa.Boolean(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("blood_pressure", sa.String(length=16), nullable=False),
        sa.Column("cholesterol_level", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["disease_id"], ["diseases.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "symptom_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("inputs", sa.JSON(), nullable=False),
        sa.Column("predictions", sa.JSON(), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "prescription_scans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("ocr_text", sa.Text(), nullable=False),
        sa.Column("matched_drug_id", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["matched_drug_id"], ["drugs.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("prescription_scans")
    op.drop_table("symptom_submissions")
    op.drop_table("patient_profiles")
    op.drop_index(op.f("ix_drugs_generic_name"), table_name="drugs")
    op.drop_index(op.f("ix_drugs_brand_name"), table_name="drugs")
    op.drop_table("drugs")
    op.drop_index(op.f("ix_diseases_slug"), table_name="diseases")
    op.drop_table("diseases")
    op.drop_index(op.f("ix_users_firebase_uid"), table_name="users")
    op.drop_table("users")
