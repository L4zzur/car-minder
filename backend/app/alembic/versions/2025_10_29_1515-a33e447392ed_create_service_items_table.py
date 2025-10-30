"""create service_items table

Revision ID: a33e447392ed
Revises: 0e6dbee037dc
Create Date: 2025-10-29 15:15:29.099056

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a33e447392ed"
down_revision: Union[str, Sequence[str], None] = "0e6dbee037dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "service_items",
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique identifier"),
        sa.Column("car_id", sa.Uuid(), nullable=False, comment="ID of the car"),
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
            comment="Name of the service item",
        ),
        sa.Column(
            "last_service_date",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Date of the last service",
        ),
        sa.Column(
            "last_service_mileage",
            sa.Integer(),
            nullable=False,
            comment="Mileage of the last service",
        ),
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
            "last_service_mileage >= 0",
            name=op.f("ck_service_items_service_item_mileage_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["car_id"],
            ["cars.id"],
            name=op.f("fk_service_items_car_id_cars"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_service_items")),
        sa.UniqueConstraint("car_id", "name", name="uq_service_items_car_name"),
    )
    op.create_index("ix_service_items_car", "service_items", ["car_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_service_items_car", table_name="service_items")
    op.drop_table("service_items")
