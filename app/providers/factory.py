import httpx

from app.core.config import Settings
from app.providers.alpha.client import AlphaProvider
from app.providers.base import VerificationProvider


class ProviderFactory:
    @staticmethod
    def create(
        provider_name: str,
        http_client: httpx.AsyncClient,
        settings: Settings,
    ) -> VerificationProvider:
        if provider_name == "alpha":
            return AlphaProvider(
                http_client=http_client,
                client_id=settings.alpha_client_id,
                client_secret=settings.alpha_client_secret,
            )

        raise ValueError(
            f"Unsupported provider: {provider_name}"
        )
