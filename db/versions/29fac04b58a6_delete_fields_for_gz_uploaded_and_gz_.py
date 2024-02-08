"""Delete fields for gz_uploaded and gz_filename

Revision ID: 29fac04b58a6
Revises: 18210c838fb9
Create Date: 2024-02-08 09:16:01.436560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '29fac04b58a6'
down_revision: Union[str, None] = '18210c838fb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('uploads', 'gz_uploaded')
    op.drop_column('uploads', 'gz_filename')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('uploads', sa.Column('gz_filename', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('uploads', sa.Column('gz_uploaded', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
