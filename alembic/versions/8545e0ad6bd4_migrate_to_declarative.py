"""Migrate to declarative

Revision ID: 8545e0ad6bd4
Revises: 7172bfcfb359
Create Date: 2023-05-19 20:33:12.730980

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "8545e0ad6bd4"
down_revision = "7172bfcfb359"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "liked_videos",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "liked_videos",
        "video_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.alter_column(
        "livestreams",
        "start_time",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
    )
    op.drop_index("ix_livestreams_title", table_name="livestreams")
    op.alter_column(
        "posts",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.drop_column("users", "last_login")
    op.drop_column("users", "last_login_ip")
    op.alter_column(
        "videos",
        "duration",
        existing_type=sa.INTEGER(),
        nullable=False,
        existing_server_default=sa.text("0"),
    )


def downgrade() -> None:
    op.alter_column(
        "videos",
        "duration",
        existing_type=sa.INTEGER(),
        nullable=True,
        existing_server_default=sa.text("0"),
    )
    op.add_column(
        "users",
        sa.Column(
            "last_login_ip",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "last_login",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.alter_column(
        "posts",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )
    op.create_index(
        "ix_livestreams_title",
        "livestreams",
        ["title"],
        unique=False,
    )
    op.alter_column(
        "livestreams",
        "start_time",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
    )
    op.alter_column(
        "liked_videos",
        "video_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )
    op.alter_column(
        "liked_videos",
        "user_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )
