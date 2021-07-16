"""Added djs table

Revision ID: 3a0190da28b1
Revises: 8bdd3a14ff24
Create Date: 2021-03-11 11:53:34.231032

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '3a0190da28b1'
down_revision = '8bdd3a14ff24'
branch_labels = None
depends_on = None


def upgrade():
# ### commands auto generated by Alembic - please adjust! ###
    op.create_table('djs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('real_name', sa.String(), nullable=True),
    sa.Column('aliases', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('member_of_groups', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('genres', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('image', sa.String(), nullable=True),
    sa.Column('birth_date', sa.Date(), nullable=True),
    sa.Column('site', sa.String(), nullable=True),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('created', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('slug')
    )
    # ### end Alembic commands ###


def downgrade():
# ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('djs')
    # ### end Alembic commands ###