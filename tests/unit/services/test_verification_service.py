from unittest.mock import AsyncMock

import pytest

from app.schemas.verification import VerificationResult
from app.services.verification import VerificationService


@pytest.mark.asyncio
async def test_service_delegates_to_provider() -> None:
    provider = AsyncMock()

    provider.verify.return_value = VerificationResult(
        verified=True,
        risk_level="low",
        provider="alpha",
    )

    service = VerificationService(
        provider=provider,
    )

    result = await service.verify(
        phone_number="+381641234567",
        correlation_id="corr-123",
    )

    provider.verify.assert_awaited_once_with(
        phone_number="+381641234567",
        correlation_id="corr-123",
    )

    assert result.verified is True
    assert result.risk_level == "low"
    assert result.provider == "alpha"
