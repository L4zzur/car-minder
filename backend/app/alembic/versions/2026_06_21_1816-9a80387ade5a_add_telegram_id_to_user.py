"""add telegram_id to user

Revision ID: 9a80387ade5a
Revises: a48914e7b43d
Create Date: 2026-06-21 18:16:25.559806

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a80387ade5a"
down_revision: str | Sequence[str] | None = "a48914e7b43d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column(
                "telegram_id",
                sa.BigInteger(),
                nullable=True,
                comment="User Telegram ID",
            )
        )
        batch_op.create_unique_constraint(op.f("uq_users_telegram_id"), ["telegram_id"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint(op.f("uq_users_telegram_id"), type_="unique")
        batch_op.drop_column("telegram_id")
