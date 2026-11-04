"""create tool and audit log tables

Revision ID: 0001
Revises: 
Create Date: 2026-10-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('audit_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('actor_id', sa.Integer(), nullable=True),
    sa.Column('action', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('entity_type', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=False),
    sa.Column('details', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tool',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('category', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tool_name'), 'tool', ['name'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tool_name'), table_name='tool')
    op.drop_table('tool')
    op.drop_table('audit_log')
