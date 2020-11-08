"""Rename channel columns and add yt_banner column

Revision ID: 04fde0adbc66
Revises: 3d756e8f5eea
Create Date: 2019-12-06 13:36:13.370610

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '04fde0adbc66'
down_revision = '3d756e8f5eea'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'channels',
        'youtube_id',
        new_column_name='yt_id',
        nullable=False
    )
    op.alter_column(
        'channels',
        'thumbnail_url',
        new_column_name='yt_thumbnail',
        nullable=False
    )
    op.add_column(
        'channels',
        sa.Column('yt_banner', sa.String(), nullable=True)
    )
    op.drop_constraint('channels_youtube_id_key', 'channels', type_='unique')
    op.create_unique_constraint('channels_yt_id_key', 'channels', ['yt_id'])


def downgrade():
    op.drop_constraint('channels_yt_id_key', 'channels', type_='unique')
    op.create_unique_constraint(
        'channels_youtube_id_key',
        'channels',
        ['youtube_id']
    )
    op.drop_column('channels', 'yt_banner')
    op.alter_column(
        'channels',
        'yt_thumbnail',
        new_column_name='thumbnail_url',
        nullable=False
    )
    op.alter_column(
        'channels',
        'yt_id',
        new_column_name='youtube_id',
        nullable=False
    )
