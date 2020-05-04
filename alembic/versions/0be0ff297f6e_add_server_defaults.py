"""Add server_defaults

Revision ID: 0be0ff297f6e
Revises: f761e61776c9
Create Date: 2020-05-04 15:56:18.145539

"""
from sqlalchemy import func

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0be0ff297f6e'
down_revision = 'f761e61776c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'is_active', server_default='f')
    op.alter_column('users', 'is_admin', server_default='f')
    op.alter_column('users', 'is_banned', server_default='f')
    op.alter_column('users', 'created', server_default=func.now())

    op.alter_column('videos', 'duration', server_default="0")

    op.alter_column('comments', 'published_at', server_default=func.now())
    op.alter_column('comments', 'deleted', server_default='f')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'is_active', server_default='')
    op.alter_column('users', 'is_admin', server_default='')
    op.alter_column('users', 'is_banned', server_default='')
    op.alter_column('users', 'created', server_default='')

    op.alter_column('videos', 'duration', server_default='')

    op.alter_column('comments', 'published_at', server_default='')
    op.alter_column('comments', 'deleted', server_default='')
    # ### end Alembic commands ###
