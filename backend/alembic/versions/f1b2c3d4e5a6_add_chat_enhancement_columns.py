"""add chat enhancement columns

Revision ID: f1b2c3d4e5a6
Revises: e7a3b1c2d4f5
Create Date: 2026-05-15 19:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'f1b2c3d4e5a6'
down_revision: Union[str, Sequence[str], None] = 'e7a3b1c2d4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # chat_sessions: add case_id FK and follow_up_count
    op.add_column('chat_sessions', sa.Column('follow_up_count', sa.Integer(), server_default='0', nullable=False))

    # Drop old case_id column if it exists without FK, re-add with FK
    op.execute('ALTER TABLE chat_sessions DROP COLUMN IF EXISTS case_id')
    op.add_column('chat_sessions', sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_chat_sessions_case_id', 'chat_sessions', 'cases', ['case_id'], ['id'])

    # chat_messages: add is_follow_up and attachments
    op.add_column('chat_messages', sa.Column('is_follow_up', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('chat_messages', sa.Column('attachments', postgresql.JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column('chat_messages', 'attachments')
    op.drop_column('chat_messages', 'is_follow_up')
    op.drop_constraint('fk_chat_sessions_case_id', 'chat_sessions', type_='foreignkey')
    op.drop_column('chat_sessions', 'case_id')
    op.drop_column('chat_sessions', 'follow_up_count')
