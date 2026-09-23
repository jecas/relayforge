from typing import Protocol

from app.schemas.verification import VerificationResult


class VerificationProvider(Protocol):
    name: str

    async def verify(
        self,
        phone_number: str,
        correlation_id: str,
    ) -> VerificationResult:
        ...
