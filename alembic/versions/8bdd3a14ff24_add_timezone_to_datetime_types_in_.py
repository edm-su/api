"""Add timezone to datetime types in livestreams

Revision ID: 8bdd3a14ff24
Revises: ff6fa37c7559
Create Date: 2021-02-15 11:52:13.743247

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "8bdd3a14ff24"
down_revision = "ff6fa37c7559"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "livestreams",
        "start_time",
        type_=sa.DateTime(timezone=True),
    )
    op.alter_column(
        "livestreams",
        "end_time",
        type_=sa.DateTime(timezone=True),
    )


def downgrade() -> None:
    op.alter_column("livestreams", "start_time", type_=sa.DateTime)
    op.alter_column("livestreams", "end_time", type_=sa.DateTime)
