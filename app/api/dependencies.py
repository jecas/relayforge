from collections.abc import AsyncIterator

import httpx
from fastapi import Depends

from app.core.config import Settings, get_settings
from app.providers.base import VerificationProvider
from app.providers.factory import ProviderFactory
from app.services.verification import VerificationService


async def get_http_client(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[httpx.AsyncClient]:
    timeout = httpx.Timeout(
        settings.alpha_timeout_seconds
    )

    async with httpx.AsyncClient(
        base_url=settings.alpha_base_url,
        timeout=timeout,
    ) as client:
        yield client


def get_provider(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
) -> VerificationProvider:
    return ProviderFactory.create(
        provider_name="alpha",
        http_client=http_client,
        settings=settings,
    )


def get_verification_service(
    provider: VerificationProvider = Depends(get_provider),
) -> VerificationService:
    return VerificationService(provider=provider)
