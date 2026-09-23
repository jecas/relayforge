import httpx

from app.core.exceptions import (
    ProviderAuthenticationError,
    ProviderNotFoundError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderUnavailableError,
)


def _parse_retry_after(
    response: httpx.Response,
) -> float | None:
    value = response.headers.get("Retry-After")

    if value is None:
        return None

    try:
        retry_after = float(value)
    except ValueError:
        return None

    if retry_after < 0:
        return None

    return retry_after


def map_provider_response_error(
    response: httpx.Response,
) -> Exception:
    status_code = response.status_code

    if status_code in {401, 403}:
        return ProviderAuthenticationError()

    if status_code == 404:
        return ProviderNotFoundError()

    if status_code == 429:
        return ProviderRateLimitError(
            retry_after_seconds=_parse_retry_after(response)
        )

    if 500 <= status_code <= 599:
        return ProviderUnavailableError()

    if 400 <= status_code <= 499:
        return ProviderRequestError()

    return ProviderUnavailableError()
