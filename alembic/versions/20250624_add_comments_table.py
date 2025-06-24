"""create comments table

Revision ID: 20250624_add_comments_table
Revises: 20250622_add_article_fav
Create Date: 2025-06-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20250624_add_comments_table'
down_revision: Union[str, Sequence[str], None] = '20250622_add_article_fav'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('body', sa.String(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.String(), nullable=True),
        sa.Column('updated_at', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['article.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('comment')
