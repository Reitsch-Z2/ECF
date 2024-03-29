"""boolean first_entry in Price model

Revision ID: 05ee725db839
Revises: c405dbfca600
Create Date: 2022-07-25 02:54:28.243795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05ee725db839'
down_revision = 'c405dbfca600'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('price', schema=None) as batch_op:
        batch_op.add_column(sa.Column('first_entry', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('price', schema=None) as batch_op:
        batch_op.drop_column('first_entry')

    # ### end Alembic commands ###
