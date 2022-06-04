"""empty message

Revision ID: e8d54d05edc5
Revises: 9b6bad3df4e8
Create Date: 2022-06-04 11:06:16.132107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8d54d05edc5'
down_revision = '9b6bad3df4e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.add_column('venue', sa.Column('talent', sa.Boolean(), nullable=True))
    op.add_column('venue', sa.Column('description', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'description')
    op.drop_column('venue', 'talent')
    op.drop_column('venue', 'website_link')
    # ### end Alembic commands ###
