"""added global and finance setup tables and added single acct to memba table

Revision ID: e1947f8bfa82
Revises: 8cb1a4b9d540
Create Date: 2020-09-30 04:19:02.111771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1947f8bfa82'
down_revision = '8cb1a4b9d540'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('finance_setup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('descr', sa.String(length=130), nullable=True),
    sa.Column('enforce', sa.Boolean(), nullable=False),
    sa.Column('archive', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('global_setup',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('organisation_name', sa.String(length=160), nullable=True),
    sa.Column('organisation_name2', sa.String(length=160), nullable=True),
    sa.Column('organisation_address', sa.String(length=160), nullable=True),
    sa.Column('organisation_address2', sa.String(length=160), nullable=True),
    sa.Column('organisation_phone', sa.String(length=160), nullable=True),
    sa.Column('organisation_email', sa.String(length=160), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('global_setup')
    op.drop_table('finance_setup')
    # ### end Alembic commands ###