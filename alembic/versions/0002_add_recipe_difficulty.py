"""add required difficulty (easy / medium / hard) to recipes

Revision ID: 0002_add_difficulty
Revises: 0001_initial
Create Date: 2026-11-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_add_difficulty"
down_revision: Union[str, Sequence[str], None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

difficulty_enum = sa.Enum(
    "easy", "medium", "hard", name="difficulty", native_enum=False, create_constraint=False
)


def upgrade() -> None:
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.add_column(
            sa.Column("difficulty", difficulty_enum, nullable=False, server_default="medium")
        )
        batch_op.create_check_constraint(
            op.f("ck_recipes_difficulty"), "difficulty IN ('easy', 'medium', 'hard')"
        )

    with op.batch_alter_table("recipes") as batch_op:
        batch_op.alter_column("difficulty", existing_type=difficulty_enum, server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("recipes") as batch_op:
        batch_op.drop_constraint(op.f("ck_recipes_difficulty"), type_="check")
        batch_op.drop_column("difficulty")
