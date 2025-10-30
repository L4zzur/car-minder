"""create users table

Revision ID: e2c771131cb0
Revises:
Create Date: 2025-10-29 00:22:02.579290

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e2c771131cb0"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("tg_id", sa.Integer(), nullable=False, comment="Telegram user ID"),
        sa.Column("name", sa.String(), nullable=False, comment="Telegram first name"),
        sa.Column("username", sa.String(), nullable=True, comment="Telegram username"),
        sa.Column(
            "is_premium",
            sa.Boolean(),
            server_default=sa.text("(FALSE)"),
            nullable=False,
            comment="Has the user bought a premium",
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
        sa.PrimaryKeyConstraint("tg_id", name=op.f("pk_users")),
        sa.UniqueConstraint("tg_id", name=op.f("uq_users_tg_id")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
