"""remove gin index

Revision ID: 7172bfcfb359
Revises: 2450624e90ee
Create Date: 2023-05-01 10:10:52.506403

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "7172bfcfb359"
down_revision = "2450624e90ee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("title_idx", table_name="videos")
    op.execute("DROP EXTENSION pg_trgm")


def downgrade() -> None:
    op.create_index("title_idx", "videos", ["title"], unique=False)
    op.execute("CREATE EXTENSION pg_trgm")
