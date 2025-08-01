"""create initial tables

Revision ID: c37ebc306486
Revises: 2f44d9bd71a2
Create Date: 2025-07-31 09:06:39.335255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c37ebc306486'
down_revision: Union[str, Sequence[str], None] = '2f44d9bd71a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.add_column('posts', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'posts', 'categories', ['category_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.drop_column('posts', 'category_id')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###
