from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VerificationAudit(Base):
    __tablename__ = "verification_audits"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    correlation_id: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    provider: Mapped[str] = mapped_column(
        String(50),
    )

    status: Mapped[str] = mapped_column(
        String(50),
    )

    risk_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
