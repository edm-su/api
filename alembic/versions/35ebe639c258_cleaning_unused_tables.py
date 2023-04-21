"""Cleaning Unused Tables

Revision ID: 35ebe639c258
Revises: 68d958550cc4
Create Date: 2020-01-17 13:24:54.601658

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "35ebe639c258"
down_revision = "68d958550cc4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("videos_genres")
    op.drop_table("djs_genres")
    op.drop_table("genres")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "djs_genres",
        sa.Column("dj_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "genre_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["dj_id"],
            ["djs.id"],
            name="djs_genres_dj_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["genre_id"],
            ["genres.id"],
            name="djs_genres_genre_id_fkey",
        ),
    )
    op.create_table(
        "videos_genres",
        sa.Column(
            "video_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "genre_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["genre_id"],
            ["genres.id"],
            name="videos_genres_genre_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["video_id"],
            ["videos.id"],
            name="videos_genres_video_id_fkey",
        ),
    )
    op.create_table(
        "genres",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("slug", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="genres_pkey"),
        sa.UniqueConstraint("slug", name="genres_slug_key"),
    )
    # ### end Alembic commands ###
