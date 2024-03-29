"""empty message

Revision ID: 2fddf33c7b91
Revises: d7dc2623ba27
Create Date: 2022-04-07 11:14:38.021824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fddf33c7b91'
down_revision = 'd7dc2623ba27'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_details', sa.Column('det_qty', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_details', 'det_qty')
    # ### end Alembic commands ###
