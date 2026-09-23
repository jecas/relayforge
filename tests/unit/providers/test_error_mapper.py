import httpx

from app.core.exceptions import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderUnavailableError,
)
from app.providers.error_mapper import map_provider_response_error


def test_maps_bad_request() -> None:
    response = httpx.Response(400)

    error = map_provider_response_error(response)

    assert isinstance(error, ProviderRequestError)


def test_maps_authentication_error() -> None:
    response = httpx.Response(401)

    error = map_provider_response_error(response)

    assert isinstance(
        error,
        ProviderAuthenticationError,
    )


def test_maps_server_error() -> None:
    response = httpx.Response(503)

    error = map_provider_response_error(response)

    assert isinstance(
        error,
        ProviderUnavailableError,
    )


def test_maps_rate_limit_retry_after() -> None:
    response = httpx.Response(
        429,
        headers={
            "Retry-After": "8",
        },
    )

    error = map_provider_response_error(response)

    assert isinstance(
        error,
        ProviderRateLimitError,
    )

    assert error.retry_after_seconds == 8.0


def test_invalid_retry_after_is_ignored() -> None:
    response = httpx.Response(
        429,
        headers={
            "Retry-After": "invalid",
        },
    )

    error = map_provider_response_error(response)

    assert isinstance(
        error,
        ProviderRateLimitError,
    )

    assert error.retry_after_seconds is None
