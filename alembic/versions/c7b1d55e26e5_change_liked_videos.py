"""change-liked-videos

Revision ID: c7b1d55e26e5
Revises: 8545e0ad6bd4
Create Date: 2023-05-22 19:03:52.210838

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "c7b1d55e26e5"
down_revision = "8545e0ad6bd4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("unique_liked_video", "liked_videos", type_="unique")
    op.drop_column("liked_videos", "id")


def downgrade() -> None:
    op.add_column(
        "liked_videos",
        sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=False),
    )
    op.create_unique_constraint(
        "unique_liked_video", "liked_videos", ["user_id", "video_id"],
    )
