import httpx

from app.core.config import Settings
from app.providers.factory import ProviderFactory
from app.repositories.verification import VerificationRepository
from app.schemas.verification import VerificationResult


class VerificationService:
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        repository: VerificationRepository,
        settings: Settings,
    ) -> None:
        self._http_client = http_client
        self._repository = repository
        self._settings = settings

    async def verify(
        self,
        phone_number: str,
        correlation_id: str,
        provider_name: str,
    ) -> VerificationResult:
        provider = ProviderFactory.create(
            provider_name=provider_name,
            http_client=self._provider_client(provider_name),
            settings=self._settings,
        )

        result = await provider.verify(
            phone_number=phone_number,
            correlation_id=correlation_id,
        )

        await self._repository.create(
            correlation_id=correlation_id,
            provider=result.provider,
            status="success",
            risk_level=result.risk_level,
        )

        return result

    def _provider_client(
        self,
        provider_name: str,
    ) -> httpx.AsyncClient:
        if provider_name == "alpha":
            self._http_client.base_url = httpx.URL(
                self._settings.alpha_base_url
            )
        elif provider_name == "beta":
            self._http_client.base_url = httpx.URL(
                self._settings.beta_base_url
            )

        return self._http_client
