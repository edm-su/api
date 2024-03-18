"""Added tokens table

Revision ID: 2ffbd3538fcf
Revises: 68877806bd50
Create Date: 2021-08-03 05:58:22.921648

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "2ffbd3538fcf"
down_revision = "68877806bd50"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=True),
        sa.Column("token", sa.String(length=64), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )


def downgrade():
    op.drop_table("users_tokens")
