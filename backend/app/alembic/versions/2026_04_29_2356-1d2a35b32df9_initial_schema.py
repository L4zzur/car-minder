"""initial schema

Revision ID: 1d2a35b32df9
Revises:
Create Date: 2026-04-29 23:56:14.086906

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1d2a35b32df9"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column(
            "username",
            sa.String(),
            nullable=False,
            comment="User display username",
        ),
        sa.Column("name", sa.String(), nullable=False, comment="User display name"),
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique identifier"),
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
            "length(trim(name)) > 0", name=op.f("ck_users_user_name_not_blank")
        ),
        sa.CheckConstraint(
            "length(trim(username)) > 0",
            name=op.f("ck_users_user_username_not_blank"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "cars",
        sa.Column("user_id", sa.Uuid(), nullable=False, comment="Owner user ID"),
        sa.Column("brand", sa.String(), nullable=False, comment="Car brand"),
        sa.Column("model", sa.String(), nullable=False, comment="Car model"),
        sa.Column("year", sa.Integer(), nullable=False, comment="Car year"),
        sa.Column(
            "initial_odometer_km",
            sa.Integer(),
            nullable=False,
            comment="Odometer reading when the car was added",
        ),
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique identifier"),
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
            "initial_odometer_km >= 0",
            name=op.f("ck_cars_car_initial_odometer_non_negative"),
        ),
        sa.CheckConstraint(
            "length(trim(brand)) > 0", name=op.f("ck_cars_car_brand_not_blank")
        ),
        sa.CheckConstraint(
            "length(trim(model)) > 0", name=op.f("ck_cars_car_model_not_blank")
        ),
        sa.CheckConstraint("year >= 1930", name=op.f("ck_cars_car_year_valid")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_cars_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cars")),
    )
    op.create_index(op.f("ix_cars_user_id"), "cars", ["user_id"], unique=False)
    op.create_table(
        "mileage_logs",
        sa.Column("car_id", sa.Uuid(), nullable=False, comment="ID of the car"),
        sa.Column(
            "odometer_km",
            sa.Integer(),
            nullable=False,
            comment="Full odometer reading in kilometers",
        ),
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique identifier"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
            comment="Date and time of creation",
        ),
        sa.CheckConstraint(
            "odometer_km >= 0",
            name=op.f("ck_mileage_logs_mileage_log_odometer_non_negative"),
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
        "ix_mileage_logs_car_created_at",
        "mileage_logs",
        ["car_id", "created_at"],
        unique=False,
    )
    op.create_table(
        "service_items",
        sa.Column("car_id", sa.Uuid(), nullable=False, comment="ID of the car"),
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
            comment="Name of the service item",
        ),
        sa.Column(
            "last_service_at",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Date of the last service",
        ),
        sa.Column(
            "last_service_odometer_km",
            sa.Integer(),
            nullable=False,
            comment="Odometer reading at the last service",
        ),
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique identifier"),
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
            "last_service_odometer_km >= 0",
            name=op.f("ck_service_items_service_item_odometer_non_negative"),
        ),
        sa.CheckConstraint(
            "length(trim(name)) > 0",
            name=op.f("ck_service_items_service_item_name_not_blank"),
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
    op.create_table(
        "reminders",
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
            "interval_km",
            sa.Integer(),
            nullable=True,
            comment="Service interval in kilometers",
        ),
        sa.Column(
            "interval_days",
            sa.Integer(),
            nullable=True,
            comment="Interval between services in days",
        ),
        sa.Column(
            "notify_before_km",
            sa.Integer(),
            nullable=True,
            comment="Notify this many kilometers before service is due",
        ),
        sa.Column(
            "notify_before_days",
            sa.Integer(),
            nullable=True,
            comment="Notify this many days before service is due",
        ),
        sa.Column(
            "note",
            sa.String(),
            nullable=True,
            comment="Additional comment or notes",
        ),
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique identifier"),
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
            "(interval_km IS NOT NULL) OR (interval_days IS NOT NULL)",
            name=op.f("ck_reminders_reminder_has_interval"),
        ),
        sa.CheckConstraint(
            "interval_days IS NULL OR interval_days > 0",
            name=op.f("ck_reminders_reminder_positive_days_interval"),
        ),
        sa.CheckConstraint(
            "interval_days IS NULL OR notify_before_days IS NULL OR notify_before_days <= interval_days",
            name=op.f(
                "ck_reminders_reminder_days_notification_threshold_within_interval"
            ),
        ),
        sa.CheckConstraint(
            "interval_km IS NULL OR interval_km > 0",
            name=op.f("ck_reminders_reminder_positive_km_interval"),
        ),
        sa.CheckConstraint(
            "interval_km IS NULL OR notify_before_km IS NULL OR notify_before_km <= interval_km",
            name=op.f(
                "ck_reminders_reminder_km_notification_threshold_within_interval"
            ),
        ),
        sa.CheckConstraint(
            "notify_before_days IS NULL OR interval_days IS NOT NULL",
            name=op.f("ck_reminders_reminder_days_notification_requires_interval"),
        ),
        sa.CheckConstraint(
            "notify_before_days IS NULL OR notify_before_days >= 0",
            name=op.f("ck_reminders_reminder_non_negative_days_notification_threshold"),
        ),
        sa.CheckConstraint(
            "notify_before_km IS NULL OR interval_km IS NOT NULL",
            name=op.f("ck_reminders_reminder_km_notification_requires_interval"),
        ),
        sa.CheckConstraint(
            "notify_before_km IS NULL OR notify_before_km >= 0",
            name=op.f("ck_reminders_reminder_non_negative_km_notification_threshold"),
        ),
        sa.ForeignKeyConstraint(
            ["service_item_id"],
            ["service_items.id"],
            name=op.f("fk_reminders_service_item_id_service_items"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reminders")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("reminders")
    op.drop_table("service_items")
    op.drop_index("ix_mileage_logs_car_created_at", table_name="mileage_logs")
    op.drop_table("mileage_logs")
    op.drop_index(op.f("ix_cars_user_id"), table_name="cars")
    op.drop_table("cars")
    op.drop_table("users")
