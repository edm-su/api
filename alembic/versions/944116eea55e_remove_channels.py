"""empty message

Revision ID: 944116eea55e
Revises: 2ffbd3538fcf
Create Date: 2022-04-27 15:39:26.496242

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "944116eea55e"
down_revision = "2ffbd3538fcf"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("videos_channel_id_fkey", "videos", type_="foreignkey")
    op.drop_column("videos", "channel_id")
    op.drop_table("channels")


def downgrade():
    op.create_table(
        "channels",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("slug", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("yt_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "yt_thumbnail", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "yt_banner", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.PrimaryKeyConstraint("id", name="channels_pkey"),
        sa.UniqueConstraint("name", name="channels_name_key"),
        sa.UniqueConstraint("slug", name="channels_slug_key"),
        sa.UniqueConstraint("yt_id", name="channels_yt_id_key"),
    )
    op.add_column(
        "videos",
        sa.Column(
            "channel_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
    )
    op.create_foreign_key(
        "videos_channel_id_fkey",
        "videos",
        "channels",
        ["channel_id"],
        ["id"],
        ondelete="CASCADE",
    )
