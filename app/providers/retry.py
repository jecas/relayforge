import asyncio
import logging
from collections.abc import Awaitable, Callable

from app.core.exceptions import (
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

logger = logging.getLogger(__name__)

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
    provider_name: str,
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    attempt = 1

    while True:
        try:
            return await operation()

        except RETRYABLE_EXCEPTIONS as exc:
            if attempt >= max_attempts:
                logger.error(
                    "Provider operation exhausted retries",
                    extra={
                        "event": "provider_retry_exhausted",
                        "provider": provider_name,
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                    },
                )
                raise

            delay = base_delay_seconds * (2 ** (attempt - 1))

            if (
                isinstance(exc, ProviderRateLimitError)
                and exc.retry_after_seconds is not None
            ):
                delay = exc.retry_after_seconds

            logger.warning(
                "Retrying provider operation",
                extra={
                    "event": "provider_retry",
                    "provider": provider_name,
                    "attempt": attempt + 1,
                    "max_attempts": max_attempts,
                    "retry_delay_seconds": delay,
                },
            )

            await asyncio.sleep(delay)

            attempt += 1
