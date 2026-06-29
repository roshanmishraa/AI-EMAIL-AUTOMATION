"""baseline

Revision ID: f2d424ef57c5
Revises: 
Create Date: 2026-06-27 13:50:55.953941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'f2d424ef57c5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ── PostgreSQL Enum types — create_type=False prevents SQLAlchemy from
#    auto-issuing CREATE TYPE; we handle that ourselves via DO blocks below. ──
emailcategory    = postgresql.ENUM('legal', 'billing', 'product_issue', 'delivery', 'refund', 'general', 'spam', 'feedback',  name='emailcategory',    create_type=False)
emailsentiment   = postgresql.ENUM('angry', 'frustrated', 'neutral', 'happy', 'sad',                                          name='emailsentiment',   create_type=False)
emailstatus      = postgresql.ENUM('new', 'processing', 'processed', 'replied', 'escalated',                                  name='emailstatus',      create_type=False)
escalationreason = postgresql.ENUM('legal', 'vip', 'low_confidence', 'angry_repeat', 'sensitive_attachment',                  name='escalationreason', create_type=False)
escalationstatus = postgresql.ENUM('open', 'in_progress', 'resolved',                                                         name='escalationstatus', create_type=False)
replysource      = postgresql.ENUM('ai', 'human',                                                                             name='replysource',      create_type=False)
threadstatus     = postgresql.ENUM('open', 'closed', 'escalated',                                                             name='threadstatus',     create_type=False)


def _create_enum(conn, name: str, values: list) -> None:
    """Idempotent CREATE TYPE … AS ENUM using a PL/pgSQL DO block."""
    values_sql = ", ".join(f"'{v}'" for v in values)
    conn.execute(sa.text(f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({values_sql});
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END $$;
    """))


def upgrade() -> None:
    conn = op.get_bind()

    # ── Create enum types (idempotent) ────────────────────────
    _create_enum(conn, 'emailcategory',    ['legal', 'billing', 'product_issue', 'delivery', 'refund', 'general', 'spam', 'feedback'])
    _create_enum(conn, 'emailsentiment',   ['angry', 'frustrated', 'neutral', 'happy', 'sad'])
    _create_enum(conn, 'emailstatus',      ['new', 'processing', 'processed', 'replied', 'escalated'])
    _create_enum(conn, 'escalationreason', ['legal', 'vip', 'low_confidence', 'angry_repeat', 'sensitive_attachment'])
    _create_enum(conn, 'escalationstatus', ['open', 'in_progress', 'resolved'])
    _create_enum(conn, 'replysource',      ['ai', 'human'])
    _create_enum(conn, 'threadstatus',     ['open', 'closed', 'escalated'])

    # ── 1. users ──────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id',          sa.Integer(),  primary_key=True, index=True),
        sa.Column('email',       sa.String(),   nullable=False, unique=True, index=True),
        sa.Column('gmail_token', sa.Text(),     nullable=True),
        sa.Column('created_at',  sa.DateTime(), nullable=True),
        sa.Column('last_seen',   sa.DateTime(), nullable=True),
        sa.Column('is_active',   sa.Boolean(),  nullable=True),
    )

    # ── 2. email_threads ──────────────────────────────────────
    op.create_table(
        'email_threads',
        sa.Column('id',              sa.Integer(), primary_key=True, index=True),
        sa.Column('gmail_thread_id', sa.String(),  unique=True, index=True, nullable=True),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status',          threadstatus, nullable=True),
        sa.Column('message_count',   sa.Integer(), nullable=True),
        sa.Column('priority_level',  sa.Integer(), nullable=True),
    )

    # ── 3. emails ─────────────────────────────────────────────
    op.create_table(
        'emails',
        sa.Column('id',               sa.Integer(),   primary_key=True, index=True),
        sa.Column('gmail_message_id', sa.String(),    unique=True, index=True, nullable=True),
        sa.Column('thread_id',        sa.String(),    index=True, nullable=True),
        sa.Column('sender',           sa.String(),    nullable=True),
        sa.Column('subject',          sa.String(),    nullable=True),
        sa.Column('body',             sa.Text(),      nullable=True),
        sa.Column('received_at',      sa.DateTime(),  nullable=True),
        sa.Column('category',         emailcategory,  nullable=True),
        sa.Column('sentiment',        emailsentiment, nullable=True),
        sa.Column('intent',           sa.Text(),      nullable=True),
        sa.Column('confidence_score', sa.Float(),     nullable=True),
        sa.Column('status',           emailstatus,    nullable=True),
        sa.Column('has_attachments',  sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('attachment_names', sa.Text(),      nullable=True, server_default='[]'),
        sa.Column('user_id',          sa.Integer(),   sa.ForeignKey('users.id'), nullable=True, index=True),
    )

    # ── 4. email_replies ──────────────────────────────────────
    op.create_table(
        'email_replies',
        sa.Column('id',               sa.Integer(),  primary_key=True, index=True),
        sa.Column('email_id',         sa.Integer(),  sa.ForeignKey('emails.id'), nullable=False),
        sa.Column('generated_by',     replysource,   nullable=True),
        sa.Column('reply_text',       sa.Text(),     nullable=True),
        sa.Column('tone_used',        sa.String(),   nullable=True),
        sa.Column('confidence_score', sa.Float(),    nullable=True),
        sa.Column('is_approved',      sa.Boolean(),  nullable=True),
        sa.Column('sent_at',          sa.DateTime(), nullable=True),
        sa.Column('created_at',       sa.DateTime(), nullable=True),
    )

    # ── 5. escalations ────────────────────────────────────────
    op.create_table(
        'escalations',
        sa.Column('id',          sa.Integer(),      primary_key=True, index=True),
        sa.Column('email_id',    sa.Integer(),      sa.ForeignKey('emails.id'), nullable=True),
        sa.Column('reason',      escalationreason,  nullable=True),
        sa.Column('status',      escalationstatus,  nullable=True),
        sa.Column('notes',       sa.String(),       nullable=True),
        sa.Column('created_at',  sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    )

    # ── 6. knowledge_base ─────────────────────────────────────
    op.create_table(
        'knowledge_base',
        sa.Column('id',          sa.Integer(), primary_key=True, index=True),
        sa.Column('title',       sa.String(),  nullable=True),
        sa.Column('source_type', sa.String(),  nullable=True),
        sa.Column('file_path',   sa.String(),  nullable=True),
        sa.Column('chunk_count', sa.Integer(), nullable=True),
        sa.Column('created_at',  sa.DateTime(timezone=True), nullable=True),
    )

    # ── 7. kb_chunks ──────────────────────────────────────────
    op.create_table(
        'kb_chunks',
        sa.Column('id',             sa.Integer(), primary_key=True, index=True),
        sa.Column('kb_id',          sa.Integer(), sa.ForeignKey('knowledge_base.id'), nullable=True),
        sa.Column('chunk_text',     sa.Text(),    nullable=True),
        sa.Column('category_tag',   sa.String(),  nullable=True),
        sa.Column('chunk_index',    sa.Integer(), nullable=True),
        sa.Column('embedding_json', sa.Text(),    nullable=True),
    )

    # ── 8. system_settings ────────────────────────────────────
    op.create_table(
        'system_settings',
        sa.Column('id',                              sa.Integer(), primary_key=True),
        sa.Column('auto_send_mode',                  sa.Boolean(), nullable=True),
        sa.Column('escalation_confidence_threshold', sa.Integer(), nullable=True),
        sa.Column('polling_interval_seconds',        sa.Integer(), nullable=True),
        sa.Column('sla_response_time_minutes',       sa.Integer(), nullable=True),
        sa.Column('sla_escalation_time_minutes',     sa.Integer(), nullable=True),
        sa.Column('working_hours_start',             sa.String(),  nullable=True),
        sa.Column('working_hours_end',               sa.String(),  nullable=True),
        sa.Column('working_days',                    sa.String(),  nullable=True),
        sa.Column('slack_notify_on_escalation',      sa.Boolean(), nullable=True),
        sa.Column('slack_notify_on_legal',           sa.Boolean(), nullable=True),
        sa.Column('agent_email',                     sa.String(),  nullable=True),
        sa.Column('email_notify_on_escalation',      sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('system_settings')
    op.drop_table('kb_chunks')
    op.drop_table('knowledge_base')
    op.drop_table('escalations')
    op.drop_table('email_replies')
    op.drop_table('emails')
    op.drop_table('email_threads')
    op.drop_table('users')
    conn = op.get_bind()
    conn.execute(sa.text("DROP TYPE IF EXISTS emailcategory"))
    conn.execute(sa.text("DROP TYPE IF EXISTS emailsentiment"))
    conn.execute(sa.text("DROP TYPE IF EXISTS emailstatus"))
    conn.execute(sa.text("DROP TYPE IF EXISTS escalationreason"))
    conn.execute(sa.text("DROP TYPE IF EXISTS escalationstatus"))
    conn.execute(sa.text("DROP TYPE IF EXISTS replysource"))
    conn.execute(sa.text("DROP TYPE IF EXISTS threadstatus"))