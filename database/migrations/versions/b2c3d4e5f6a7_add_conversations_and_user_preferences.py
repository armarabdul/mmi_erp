"""add_conversations_and_user_preferences

Revision ID: b2c3d4e5f6a7
Revises: ac3b07a83700
Create Date: 2026-09-29 11:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'ac3b07a83700'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ### conversation_messages ###
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('conversation_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('user_message', sa.Text(), nullable=False),
        sa.Column('assistant_response', sa.Text(), nullable=False),
        sa.Column('detected_intent', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('audit_reference', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index('ix_conversation_messages_id', 'conversation_messages', ['id'], unique=False)
    op.create_index('ix_conversation_messages_conversation_id', 'conversation_messages', ['conversation_id'], unique=False)
    op.create_index('ix_conversation_messages_user_id', 'conversation_messages', ['user_id'], unique=False)
    op.create_index('ix_conversation_messages_timestamp', 'conversation_messages', ['timestamp'], unique=False)
    op.create_index('idx_conversation_user', 'conversation_messages', ['conversation_id', 'user_id'], unique=False)

    # ### user_preferences ###
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('preferred_language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('preferred_response_style', sa.String(length=50), nullable=True, server_default='concise'),
        sa.Column('preferred_report_format', sa.String(length=50), nullable=True, server_default='table_and_chart'),
        sa.Column('terminology_preference', sa.String(length=50), nullable=True, server_default='standard'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )
    op.create_index('ix_user_preferences_id', 'user_preferences', ['id'], unique=False)
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'], unique=True)

def downgrade() -> None:
    op.drop_table('user_preferences')
    op.drop_table('conversation_messages')
