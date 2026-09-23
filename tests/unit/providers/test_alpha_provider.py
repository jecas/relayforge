import json

import httpx
import pytest

from app.providers.alpha.client import AlphaProvider


@pytest.mark.asyncio
async def test_alpha_provider_executes_full_flow() -> None:
    requests: list[httpx.Request] = []

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        requests.append(request)

        if request.url.path == "/oauth/authorize":
            return httpx.Response(
                200,
                json={
                    "auth_req_id": "auth-123",
                },
            )

        if request.url.path == "/oauth/token":
            return httpx.Response(
                200,
                json={
                    "access_token": "token-456",
                    "token_type": "Bearer",
                },
            )

        if request.url.path == "/verify":
            return httpx.Response(
                200,
                json={
                    "match": True,
                    "risk_score": 18,
                },
            )

        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://alpha.test",
    ) as client:
        provider = AlphaProvider(
            http_client=client,
            client_id="client-id",
            client_secret="client-secret",
        )

        result = await provider.verify(
            phone_number="+381641234567",
            correlation_id="corr-123",
        )

    assert result.verified is True
    assert result.risk_level == "low"
    assert result.provider == "alpha"

    assert len(requests) == 3

    authorize_request = requests[0]

    assert authorize_request.url.path == "/oauth/authorize"
    assert (
        authorize_request.headers["X-Correlation-ID"]
        == "corr-123"
    )

    authorize_body = json.loads(
        authorize_request.content
    )

    assert authorize_body == {
        "login_hint": "+381641234567",
        "client_id": "client-id",
    }

    token_request = requests[1]

    assert token_request.url.path == "/oauth/token"
    assert (
        token_request.headers["X-Correlation-ID"]
        == "corr-123"
    )

    verify_request = requests[2]

    assert verify_request.url.path == "/verify"

    assert (
        verify_request.headers["Authorization"]
        == "Bearer token-456"
    )

    assert (
        verify_request.headers["X-Correlation-ID"]
        == "corr-123"
    )
