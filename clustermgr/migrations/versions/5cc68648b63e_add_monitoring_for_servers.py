"""add monitoring for servers

Revision ID: 5cc68648b63e
Revises: 0e7453df1644
Create Date: 2018-03-22 00:25:13.247188

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cc68648b63e'
down_revision = '0e7453df1644'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('server', schema=None) as batch_op:
        batch_op.add_column(sa.Column('monitoring', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('server', schema=None) as batch_op:
        batch_op.drop_column('monitoring')

    # ### end Alembic commands ###
