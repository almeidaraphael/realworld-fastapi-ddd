"""create article_favorite table

Revision ID: 20250622_add_article_fav
Revises: 20250622_add_articles_table
Create Date: 2025-06-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20250622_add_article_fav'
down_revision: Union[str, Sequence[str], None] = '20250622_add_articles_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('article_favorite',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'article_id')
    )

def downgrade() -> None:
    op.drop_table('article_favorite')
