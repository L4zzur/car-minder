"""create reminders table

Revision ID: 17c4722ffefa
Revises: 6671abca8548
Create Date: 2025-10-30 14:01:24.745485

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "17c4722ffefa"
down_revision: Union[str, Sequence[str], None] = "6671abca8548"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "reminders",
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique identifier"),
        sa.Column("car_id", sa.Uuid(), nullable=False, comment="ID of the car"),
        sa.Column(
            "service_item_id",
            sa.Uuid(),
            nullable=False,
            comment="ID of the service item",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("(TRUE)"),
            nullable=False,
            comment="Is the reminder active",
        ),
        sa.Column(
            "interval_mileage",
            sa.Integer(),
            nullable=True,
            comment="Interval between services in km",
        ),
        sa.Column(
            "interval_days",
            sa.Integer(),
            nullable=True,
            comment="Interval between services in days",
        ),
        sa.Column(
            "warning_mileage_before",
            sa.Integer(),
            nullable=True,
            comment="Warn X km before service due",
        ),
        sa.Column(
            "warning_days_before",
            sa.Integer(),
            nullable=True,
            comment="Warn X days before service due",
        ),
        sa.Column(
            "comment",
            sa.String(),
            nullable=True,
            comment="Additional comment or notes",
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
            "(interval_mileage IS NOT NULL) OR (interval_days IS NOT NULL)",
            name=op.f("ck_reminders_reminder_has_interval"),
        ),
        sa.CheckConstraint(
            "interval_days IS NULL OR interval_days > 0",
            name=op.f("ck_reminders_reminder_positive_days_interval"),
        ),
        sa.CheckConstraint(
            "interval_mileage IS NULL OR interval_mileage > 0",
            name=op.f("ck_reminders_reminder_positive_mileage_interval"),
        ),
        sa.CheckConstraint(
            "warning_days_before IS NULL OR warning_days_before >= 0",
            name=op.f("ck_reminders_reminder_non_negative_days_warning"),
        ),
        sa.CheckConstraint(
            "warning_mileage_before IS NULL OR warning_mileage_before >= 0",
            name=op.f("ck_reminders_reminder_non_negative_mileage_warning"),
        ),
        sa.ForeignKeyConstraint(
            ["car_id"],
            ["cars.id"],
            name=op.f("fk_reminders_car_id_cars"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["service_item_id"],
            ["service_items.id"],
            name=op.f("fk_reminders_service_item_id_service_items"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reminders")),
    )
    op.create_index(
        "ix_reminders_car_active",
        "reminders",
        ["car_id", "is_active"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_reminders_car_active", table_name="reminders")
    op.drop_table("reminders")
