"""add telegram_id to user

Revision ID: 9a80387ade5a
Revises: a48914e7b43d
Create Date: 2026-06-21 18:16:25.559806

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a80387ade5a"
down_revision: Union[str, Sequence[str], None] = "a48914e7b43d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "telegram_id",
            sa.BigInteger(),
            nullable=True,
            comment="User Telegram ID",
        ),
    )
    op.create_unique_constraint(op.f("uq_users_telegram_id"), "users", ["telegram_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_users_telegram_id"), "users", type_="unique")
    op.drop_column("users", "telegram_id")
