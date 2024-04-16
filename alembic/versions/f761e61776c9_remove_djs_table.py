"""Remove djs table

Revision ID: f761e61776c9
Revises: 9ac61fa239aa
Create Date: 2020-04-30 16:59:02.386588

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f761e61776c9"
down_revision = "9ac61fa239aa"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("djs_videos")
    op.drop_table("social_pages")
    op.drop_table("djs")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "social_pages",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("url", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "network",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("dj_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["dj_id"],
            ["djs.id"],
            name="social_pages_dj_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="social_pages_pkey"),
    )
    op.create_table(
        "djs",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("slug", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("image", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("country", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="djs_pkey"),
        sa.UniqueConstraint("image", name="djs_image_key"),
        sa.UniqueConstraint("name", name="djs_name_key"),
        sa.UniqueConstraint("slug", name="djs_slug_key"),
    )
    op.create_table(
        "djs_videos",
        sa.Column("dj_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "video_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["dj_id"],
            ["djs.id"],
            name="djs_videos_dj_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["video_id"],
            ["videos.id"],
            name="djs_videos_video_id_fkey",
        ),
    )
    # ### end Alembic commands ###
