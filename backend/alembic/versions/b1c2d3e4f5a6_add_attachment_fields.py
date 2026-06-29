"""add attachment fields to emails

Revision ID: b1c2d3e4f5a6
Revises: a26f4e615eb8
Create Date: 2026-06-28 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = 'a26f4e615eb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass  # columns already in baseline migration


def downgrade() -> None:
    pass