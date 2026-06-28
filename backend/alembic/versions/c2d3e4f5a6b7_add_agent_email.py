"""add agent email and smtp notification settings

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-06-28 00:01:00.000000

HOW TO RUN:
  cd backend
  alembic upgrade head
"""
# ============================================================
# FILE:  backend/alembic/versions/c2d3e4f5a6b7_add_agent_email.py
# NEW FILE — copy into versions/ folder
# ============================================================

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision:       str                     = 'c2d3e4f5a6b7'
down_revision:  Union[str, None]        = 'b1c2d3e4f5a6'
branch_labels:  Union[str, Sequence[str], None] = None
depends_on:     Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Agent email address for escalation pings
    op.add_column(
        'system_settings',
        sa.Column('agent_email', sa.String(), nullable=True, server_default='')
    )

    # Toggle for email notifications (separate from Slack)
    op.add_column(
        'system_settings',
        sa.Column('email_notify_on_escalation', sa.Boolean(), nullable=False, server_default='1')
    )


def downgrade() -> None:
    op.drop_column('system_settings', 'email_notify_on_escalation')
    op.drop_column('system_settings', 'agent_email')