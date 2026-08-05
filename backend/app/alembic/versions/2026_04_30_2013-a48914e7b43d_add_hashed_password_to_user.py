"""add hashed_password to user

Revision ID: a48914e7b43d
Revises: 1d2a35b32df9
Create Date: 2026-04-30 20:13:20.596540

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a48914e7b43d"
down_revision: str | Sequence[str] | None = "1d2a35b32df9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "hashed_password",
            sa.String(),
            nullable=False,
            comment="Password hash",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "hashed_password")
