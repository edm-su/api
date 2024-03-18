"""Column nickname renamed to username

Revision ID: e548b42691f0
Revises: c56146eaf110
Create Date: 2020-01-10 16:28:25.218796

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "e548b42691f0"
down_revision = "c56146eaf110"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("users", "nickname", new_column_name="username")


def downgrade():
    op.alter_column("users", "username", new_column_name="nickname")
