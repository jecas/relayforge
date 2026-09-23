from unittest.mock import AsyncMock, patch

import pytest

from app.core.exceptions import (
    ProviderAuthenticationError,
    ProviderUnavailableError,
)
from app.providers.retry import with_retry


@pytest.mark.asyncio
async def test_retries_retryable_exception() -> None:
    operation = AsyncMock(
        side_effect=[
            ProviderUnavailableError(),
            ProviderUnavailableError(),
            "success",
        ]
    )

    with patch(
        "app.providers.retry.asyncio.sleep",
        new_callable=AsyncMock,
    ) as sleep:
        result = await with_retry(
            operation,
            max_attempts=3,
            base_delay_seconds=0.5,
        )

    assert result == "success"
    assert operation.await_count == 3

    assert sleep.await_count == 2
    sleep.assert_any_await(0.5)
    sleep.assert_any_await(1.0)


@pytest.mark.asyncio
async def test_does_not_retry_non_retryable_exception() -> None:
    operation = AsyncMock(
        side_effect=ProviderAuthenticationError()
    )

    with pytest.raises(
        ProviderAuthenticationError
    ):
        await with_retry(
            operation,
            max_attempts=3,
            base_delay_seconds=0,
        )

    assert operation.await_count == 1


@pytest.mark.asyncio
async def test_stops_after_max_attempts() -> None:
    operation = AsyncMock(
        side_effect=ProviderUnavailableError()
    )

    with patch(
        "app.providers.retry.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        with pytest.raises(
            ProviderUnavailableError
        ):
            await with_retry(
                operation,
                max_attempts=3,
                base_delay_seconds=0,
            )

    assert operation.await_count == 3
