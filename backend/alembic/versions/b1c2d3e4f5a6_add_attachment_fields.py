"""add attachment fields to emails

Revision ID: b1c2d3e4f5a6
Revises: a26f4e615eb8
Create Date: 2026-06-28 00:00:00.000000

HOW TO RUN:
  cd backend
  alembic upgrade head
"""
# ============================================================
# FILE:  backend/alembic/versions/b1c2d3e4f5a6_add_attachment_fields.py
# NEW FILE — copy this as-is into the versions/ folder
# ============================================================

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision:       str                     = 'b1c2d3e4f5a6'
down_revision:  Union[str, None]        = 'a26f4e615eb8'   # ← last migration
branch_labels:  Union[str, Sequence[str], None] = None
depends_on:     Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add has_attachments column (Boolean, default False)
    op.add_column(
        'emails',
        sa.Column('has_attachments', sa.Boolean(), nullable=False, server_default='0')
    )

    # Add attachment_names column (Text, default empty JSON array)
    op.add_column(
        'emails',
        sa.Column('attachment_names', sa.Text(), nullable=True, server_default='[]')
    )


def downgrade() -> None:
    op.drop_column('emails', 'attachment_names')
    op.drop_column('emails', 'has_attachments')