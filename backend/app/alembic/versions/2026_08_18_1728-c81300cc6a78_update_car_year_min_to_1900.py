"""update_car_year_min_to_1900

Revision ID: c81300cc6a78
Revises: a65541b7f34c
Create Date: 2026-08-18 17:28:34.064098

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c81300cc6a78"
down_revision: str | Sequence[str] | None = "a65541b7f34c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("cars", schema=None) as batch_op:
        batch_op.drop_constraint("ck_cars_car_year_valid", type_="check")
        batch_op.create_check_constraint(
            "ck_cars_car_year_valid",
            "year >= 1900",
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("cars", schema=None) as batch_op:
        batch_op.drop_constraint("ck_cars_car_year_valid", type_="check")
        batch_op.create_check_constraint(
            "ck_cars_car_year_valid",
            "year >= 1930",
        )
