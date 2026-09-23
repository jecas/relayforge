from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "verification_audits",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "correlation_id",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "provider",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "risk_level",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_verification_audits_correlation_id",
        "verification_audits",
        ["correlation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_verification_audits_correlation_id",
        table_name="verification_audits",
    )

    op.drop_table(
        "verification_audits"
    )
