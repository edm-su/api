"""Remove djs

Revision ID: 3e42d8173db1
Revises: 944116eea55e
Create Date: 2023-04-12 15:50:34.156373

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "3e42d8173db1"
down_revision = "944116eea55e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("livestreams", "djs")
    op.drop_table("groups_members")
    op.drop_table("djs")


def downgrade() -> None:
    pass
