from collections.abc import AsyncIterator

import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.repositories.verification import VerificationRepository
from app.services.verification import VerificationService


async def get_http_client(
    settings: Settings = Depends(get_settings),
) -> AsyncIterator[httpx.AsyncClient]:
    timeout = httpx.Timeout(
        max(
            settings.alpha_timeout_seconds,
            settings.beta_timeout_seconds,
        )
    )

    async with httpx.AsyncClient(
        timeout=timeout,
    ) as client:
        yield client


def get_verification_service(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> VerificationService:
    repository = VerificationRepository(session)

    return VerificationService(
        http_client=http_client,
        repository=repository,
        settings=settings,
    )
