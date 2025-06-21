"""create follower table

Revision ID: 20250622_add_followers_table
Revises: 20250622_add_users_table
Create Date: 2025-06-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20250622_add_followers_table'
down_revision: Union[str, Sequence[str], None] = '20250622_add_users_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('follower',
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('followee_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['followee_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('follower_id', 'followee_id')
    )

def downgrade() -> None:
    op.drop_table('follower')
