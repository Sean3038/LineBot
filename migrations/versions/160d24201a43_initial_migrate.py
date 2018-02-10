"""initial migrate

Revision ID: 160d24201a43
Revises: 
Create Date: 2018-01-30 17:59:58.012590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '160d24201a43'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user')
    )
    op.create_table('observables',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=20), nullable=False),
    sa.Column('user_id', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.user'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('observables')
    op.drop_table('users')
    # ### end Alembic commands ###
