from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from app.core.config import Settings
from app.schemas.verification import VerificationResult
from app.services.verification import VerificationService


@pytest.mark.asyncio
async def test_service_uses_selected_provider_and_persists_audit() -> None:
    http_client = Mock(spec=httpx.AsyncClient)
    http_client.base_url = httpx.URL("https://provider.test")

    repository = AsyncMock()

    provider = AsyncMock()
    provider.verify.return_value = VerificationResult(
        verified=True,
        risk_level="low",
        provider="alpha",
    )

    settings = Settings(
        alpha_base_url="https://alpha.test",
    )

    service = VerificationService(
        http_client=http_client,
        repository=repository,
        settings=settings,
    )

    with patch(
        "app.services.verification.ProviderFactory.create",
        return_value=provider,
    ) as factory:
        result = await service.verify(
            phone_number="+381641234567",
            correlation_id="corr-123",
            provider_name="alpha",
        )

    factory.assert_called_once()

    provider.verify.assert_awaited_once_with(
        phone_number="+381641234567",
        correlation_id="corr-123",
    )

    repository.create.assert_awaited_once_with(
        correlation_id="corr-123",
        provider="alpha",
        status="success",
        risk_level="low",
    )

    assert result.verified is True
