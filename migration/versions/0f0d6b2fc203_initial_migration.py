"""initial migration

Revision ID: 0f0d6b2fc203
Revises: 
Create Date: 2024-09-21 11:01:34.217065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f0d6b2fc203'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Posts',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('upvotes', sa.Integer(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Posts_id'), 'Posts', ['id'], unique=False)
    op.create_table('Comments',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('upvotes', sa.Integer(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('post_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['Posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Comments_id'), 'Comments', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_Comments_id'), table_name='Comments')
    op.drop_table('Comments')
    op.drop_index(op.f('ix_Posts_id'), table_name='Posts')
    op.drop_table('Posts')
    # ### end Alembic commands ###
