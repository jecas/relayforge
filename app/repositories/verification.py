from sqlalchemy.ext.asyncio import AsyncSession

from app.models.verification import VerificationAudit


class VerificationRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        *,
        correlation_id: str,
        provider: str,
        status: str,
        risk_level: str | None,
    ) -> VerificationAudit:
        audit = VerificationAudit(
            correlation_id=correlation_id,
            provider=provider,
            status=status,
            risk_level=risk_level,
        )

        self._session.add(audit)
        await self._session.commit()
        await self._session.refresh(audit)

        return audit
