"""create cars table

Revision ID: 0e6dbee037dc
Revises: e2c771131cb0
Create Date: 2025-10-29 00:47:23.439930

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0e6dbee037dc"
down_revision: Union[str, Sequence[str], None] = "e2c771131cb0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cars",
        sa.Column("id", sa.Uuid(), nullable=False, comment="Unique identifier"),
        sa.Column(
            "user_tg_id",
            sa.Integer(),
            nullable=False,
            comment="Telegram ID of the user",
        ),
        sa.Column("brand", sa.String(), nullable=False, comment="Car brand"),
        sa.Column("model", sa.String(), nullable=False, comment="Car model"),
        sa.Column("year", sa.Integer(), nullable=False, comment="Car year"),
        sa.Column(
            "first_mileage",
            sa.Integer(),
            nullable=False,
            comment="First mileage at adding to the bot",
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
            "year >= 1930 AND year <= CAST(strftime('%Y','now') AS INTEGER)",
            name=op.f("ck_cars_car_year_valid"),
        ),
        sa.ForeignKeyConstraint(
            ["user_tg_id"],
            ["users.tg_id"],
            name=op.f("fk_cars_user_tg_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cars")),
    )
    op.create_index(op.f("ix_cars_user_tg_id"), "cars", ["user_tg_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_cars_user_tg_id"), table_name="cars")
    op.drop_table("cars")
