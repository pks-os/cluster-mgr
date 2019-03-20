"""add CacheServer model

Revision ID: edb3a875fde8
Revises: dfb03ed2c00d
Create Date: 2019-03-14 23:50:29.847675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'edb3a875fde8'
down_revision = 'dfb03ed2c00d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cache_server',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hostname', sa.String(length=250), nullable=True),
    sa.Column('ip', sa.String(length=45), nullable=True),
    sa.Column('install_redis', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('cache_server')
    # ### end Alembic commands ###