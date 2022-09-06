"""removed test column

Revision ID: a0f3176971f0
Revises: 3a49a4ea52d4
Create Date: 2022-09-06 19:50:48.382934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0f3176971f0'
down_revision = '3a49a4ea52d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Account', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['Id'])

    with op.batch_alter_table('Currency', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['Id'])
        batch_op.drop_column('Test')

    with op.batch_alter_table('Rating', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['Id'])

    with op.batch_alter_table('Transactions', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['Id'])

    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['Id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('Transactions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('Rating', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('Currency', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Test', sa.VARCHAR(length=10), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('Account', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###