"""Add project detail fields to project_records

Revision ID: 20260320_000002
Revises: 20260320_000001
Create Date: 2026-03-20 23:40:00

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260320_000002"
down_revision = "20260320_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("project_records", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("project_records", sa.Column("video_url", sa.Text(), nullable=True))
    op.add_column("project_records", sa.Column("category", sa.String(length=120), nullable=True))
    op.create_index(op.f("ix_project_records_category"), "project_records", ["category"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_project_records_category"), table_name="project_records")
    op.drop_column("project_records", "category")
    op.drop_column("project_records", "video_url")
    op.drop_column("project_records", "description")
