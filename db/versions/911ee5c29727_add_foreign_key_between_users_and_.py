"""Add foreign key between users and upload table

Revision ID: 911ee5c29727
Revises: f820964f4daf
Create Date: 2024-01-04 07:17:05.436794

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "911ee5c29727"
down_revision: Union[str, None] = "f820964f4daf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_uploads_user_id", table_name="uploads")
    op.create_foreign_key(
        None, "uploads", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "uploads", type_="foreignkey")
    op.create_index("ix_uploads_user_id", "uploads", ["user_id"], unique=False)
    # ### end Alembic commands ###
