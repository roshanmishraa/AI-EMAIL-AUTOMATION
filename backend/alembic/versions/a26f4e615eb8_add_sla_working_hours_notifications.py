"""add sla working hours notifications

Revision ID: a26f4e615eb8
Revises: f2d424ef57c5
Create Date: 2026-06-27 13:55:07.684994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a26f4e615eb8'
down_revision: Union[str, None] = 'f2d424ef57c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass