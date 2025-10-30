"""create mileage_logs table

Revision ID: 6671abca8548
Revises: a33e447392ed
Create Date: 2025-10-29 15:16:32.276995

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6671abca8548"
down_revision: Union[str, Sequence[str], None] = "a33e447392ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "mileage_logs",
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique identifier"),
        sa.Column("car_id", sa.Uuid(), nullable=False, comment="ID of the car"),
        sa.Column("mileage", sa.Integer(), nullable=False, comment="Mileage"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
            comment="Date and time of creation",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
            comment="Date and time of last update",
        ),
        sa.CheckConstraint(
            "mileage >= 0", name=op.f("ck_mileage_logs_mileage_non_negative")
        ),
        sa.ForeignKeyConstraint(
            ["car_id"],
            ["cars.id"],
            name=op.f("fk_mileage_logs_car_id_cars"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_mileage_logs")),
    )
    op.create_index(
        "ix_mileage_logs_car_created_at_desc",
        "mileage_logs",
        ["car_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_mileage_logs_car_created_at_desc", table_name="mileage_logs")
    op.drop_table("mileage_logs")
