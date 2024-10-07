"""Add field for exclude from mapping for problematic files

Revision ID: 37f6fa13f2eb
Revises: be094b7d616e
Create Date: 2024-10-07 10:39:55.274125

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "37f6fa13f2eb"
down_revision: Union[str, None] = "be094b7d616e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "sequencing_files_uploaded",
        sa.Column("exclude_from_mapping", sa.Boolean(), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("sequencing_files_uploaded", "exclude_from_mapping")
    # ### end Alembic commands ###
