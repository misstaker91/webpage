"""empty message

Revision ID: b7403bc17d66
Revises: 5ae6dd727326
Create Date: 2021-12-08 15:06:32.268138

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7403bc17d66'
down_revision = '5ae6dd727326'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('association', sa.Column('infobody', sa.String(length=250), nullable=True))
    op.drop_column('association', 'popisek_dne')
    op.drop_column('dates', 'popisek_dne')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dates', sa.Column('popisek_dne', sa.VARCHAR(length=250), nullable=True))
    op.add_column('association', sa.Column('popisek_dne', sa.VARCHAR(length=250), nullable=True))
    op.drop_column('association', 'infobody')
    # ### end Alembic commands ###