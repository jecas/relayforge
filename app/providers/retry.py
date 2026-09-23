import asyncio
from collections.abc import Awaitable, Callable

from app.core.exceptions import (
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

RETRYABLE_EXCEPTIONS = (
    ProviderTimeoutError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


async def with_retry[T](
    operation: Callable[[], Awaitable[T]],
    *,
    max_attempts: int,
    base_delay_seconds: float,
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    attempt = 1

    while True:
        try:
            return await operation()

        except RETRYABLE_EXCEPTIONS:
            if attempt >= max_attempts:
                raise

            delay = base_delay_seconds * (2 ** (attempt - 1))

            await asyncio.sleep(delay)

            attempt += 1
