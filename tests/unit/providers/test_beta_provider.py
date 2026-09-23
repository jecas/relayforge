import httpx
import pytest

from app.providers.beta.client import BetaProvider


@pytest.mark.asyncio
async def test_beta_provider_verifies_phone() -> None:
    captured_request: httpx.Request | None = None

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal captured_request
        captured_request = request

        return httpx.Response(
            200,
            json={
                "valid": True,
                "confidence": 91,
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://beta.test",
    ) as client:
        provider = BetaProvider(
            http_client=client,
            base_url="https://beta.example.com",
            api_key="beta-secret",
            retry_base_delay_seconds=0,
        )

        result = await provider.verify(
            phone_number="+381641234567",
            correlation_id="corr-beta-123",
        )

    assert result.verified is True
    assert result.risk_level == "low"
    assert result.provider == "beta"

    assert captured_request is not None

    assert (
        captured_request.headers["X-API-Key"]
        == "beta-secret"
    )

    assert (
        captured_request.headers["x-correlation-id"]
        == "corr-beta-123"
    )
