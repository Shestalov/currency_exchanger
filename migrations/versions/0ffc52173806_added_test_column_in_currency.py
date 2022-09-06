"""added test column in currency

Revision ID: 0ffc52173806
Revises: a0f3176971f0
Create Date: 2022-09-06 19:53:56.601232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ffc52173806'
down_revision = 'a0f3176971f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Currency', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Test', sa.String(length=10), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Currency', schema=None) as batch_op:
        batch_op.drop_column('Test')

    # ### end Alembic commands ###