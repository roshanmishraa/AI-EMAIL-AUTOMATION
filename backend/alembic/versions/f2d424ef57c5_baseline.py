"""baseline

Revision ID: f2d424ef57c5
Revises: 
Create Date: 2026-06-27 13:50:55.953941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f2d424ef57c5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass