import httpx

from app.core.exceptions import (
    ProviderAuthenticationError,
    ProviderNotFoundError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderUnavailableError,
)


def map_provider_response_error(
    response: httpx.Response,
) -> Exception:
    status_code = response.status_code

    if status_code in {401, 403}:
        return ProviderAuthenticationError()

    if status_code == 404:
        return ProviderNotFoundError()

    if status_code == 429:
        return ProviderRateLimitError()

    if 500 <= status_code <= 599:
        return ProviderUnavailableError()

    if 400 <= status_code <= 499:
        return ProviderRequestError()

    return ProviderUnavailableError()
