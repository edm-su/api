"""Change text column type in posts table

Revision ID: 6b5432d5749e
Revises: 1001e80b684b
Create Date: 2020-11-15 07:10:42.226178

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6b5432d5749e'
down_revision = '1001e80b684b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('posts', 'text')
    op.add_column(
        'posts',
        sa.Column('text', sa.JSON, nullable=False, server_default='{}'),
    )
    op.alter_column('posts', 'text', server_default=None)


def downgrade() -> None:
    op.drop_column('posts', 'text')
    op.add_column(
        'posts',
        sa.Column('text', sa.String, nullable=False, server_default='t'),
    )
    op.alter_column('posts', 'text', server_default=None)
