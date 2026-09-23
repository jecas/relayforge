from app.providers.base import VerificationProvider
from app.schemas.verification import VerificationResult


class VerificationService:
    def __init__(
        self,
        provider: VerificationProvider,
    ) -> None:
        self._provider = provider

    async def verify(
        self,
        phone_number: str,
        correlation_id: str,
    ) -> VerificationResult:
        return await self._provider.verify(
            phone_number=phone_number,
            correlation_id=correlation_id,
        )
