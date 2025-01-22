"""add is_blocked_in_russia flag

Revision ID: a4b5b35350f0
Revises: fc3b4ccee21e
Create Date: 2025-01-22 22:03:48.982398

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a4b5b35350f0"
down_revision = "fc3b4ccee21e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "videos",
        sa.Column("is_blocked_in_russia", sa.Boolean(), server_default="f"),
    )


def downgrade():
    op.drop_column("videos", "is_blocked_in_russia")
