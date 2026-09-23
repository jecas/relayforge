import json

import httpx
import pytest

from app.core.exceptions import (
    ProviderAuthenticationError,
    ProviderProtocolError,
    ProviderRequestError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
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
        authorize_request.headers["x-correlation-id"]
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
        token_request.headers["x-correlation-id"]
        == "corr-123"
    )

    verify_request = requests[2]

    assert verify_request.url.path == "/verify"

    assert (
        verify_request.headers["Authorization"]
        == "Bearer token-456"
    )

    assert (
        verify_request.headers["x-correlation-id"]
        == "corr-123"
    )

@pytest.mark.asyncio
async def test_does_not_retry_authentication_error() -> None:
    request_count = 0

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        return httpx.Response(
            401,
            json={
                "error": "invalid_client",
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://alpha.test",
    ) as client:
        provider = AlphaProvider(
            http_client=client,
            client_id="client-id",
            client_secret="client-secret",
            max_attempts=3,
            retry_base_delay_seconds=0,
        )

        with pytest.raises(
            ProviderAuthenticationError
        ):
            await provider.verify(
                phone_number="+381641234567",
                correlation_id="corr-123",
            )

    assert request_count == 1


@pytest.mark.asyncio
async def test_retries_provider_unavailable_error() -> None:
    request_count = 0

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        return httpx.Response(
            503,
            json={
                "error": "temporarily_unavailable",
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://alpha.test",
    ) as client:
        provider = AlphaProvider(
            http_client=client,
            client_id="client-id",
            client_secret="client-secret",
            max_attempts=3,
            retry_base_delay_seconds=0,
        )

        with pytest.raises(
            ProviderUnavailableError
        ):
            await provider.verify(
                phone_number="+381641234567",
                correlation_id="corr-123",
            )

    assert request_count == 3


@pytest.mark.asyncio
async def test_succeeds_after_retry() -> None:
    authorize_attempts = 0

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal authorize_attempts

        if request.url.path == "/oauth/authorize":
            authorize_attempts += 1

            if authorize_attempts == 1:
                return httpx.Response(
                    503,
                    json={
                        "error": "temporarily_unavailable",
                    },
                )

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
                    "risk_score": 20,
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
            max_attempts=3,
            retry_base_delay_seconds=0,
        )

        result = await provider.verify(
            phone_number="+381641234567",
            correlation_id="corr-123",
        )

    assert authorize_attempts == 2
    assert result.verified is True


@pytest.mark.asyncio
async def test_retries_timeout() -> None:
    request_count = 0

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        raise httpx.ReadTimeout(
            "Provider timed out",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://alpha.test",
    ) as client:
        provider = AlphaProvider(
            http_client=client,
            client_id="client-id",
            client_secret="client-secret",
            max_attempts=3,
            retry_base_delay_seconds=0,
        )

        with pytest.raises(
            ProviderTimeoutError
        ):
            await provider.verify(
                phone_number="+381641234567",
                correlation_id="corr-123",
            )

    assert request_count == 3


@pytest.mark.asyncio
async def test_invalid_provider_payload_is_protocol_error() -> None:
    request_count = 0

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        return httpx.Response(
            200,
            json={
                "unexpected": "response",
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://alpha.test",
    ) as client:
        provider = AlphaProvider(
            http_client=client,
            client_id="client-id",
            client_secret="client-secret",
            max_attempts=3,
            retry_base_delay_seconds=0,
        )

        with pytest.raises(
            ProviderProtocolError
        ):
            await provider.verify(
                phone_number="+381641234567",
                correlation_id="corr-123",
            )

    assert request_count == 1

@pytest.mark.asyncio
async def test_does_not_retry_bad_request() -> None:
    request_count = 0

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal request_count
        request_count += 1

        return httpx.Response(
            400,
            json={
                "error": "invalid_request",
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://alpha.test",
    ) as client:
        provider = AlphaProvider(
            http_client=client,
            client_id="client-id",
            client_secret="client-secret",
            max_attempts=3,
            retry_base_delay_seconds=0,
        )

        with pytest.raises(
            ProviderRequestError
        ):
            await provider.verify(
                phone_number="+381641234567",
                correlation_id="corr-123",
            )

    assert request_count == 1
