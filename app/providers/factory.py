import httpx

from app.core.config import Settings
from app.providers.alpha.client import AlphaProvider
from app.providers.base import VerificationProvider
from app.providers.beta.client import BetaProvider


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
                max_attempts=settings.provider_max_attempts,
                retry_base_delay_seconds=(
                    settings.provider_retry_base_delay_seconds
                ),
            )

        if provider_name == "beta":
            return BetaProvider(
                http_client=http_client,
                api_key=settings.beta_api_key,
                max_attempts=settings.provider_max_attempts,
                retry_base_delay_seconds=(
                    settings.provider_retry_base_delay_seconds
                ),
            )

        raise ValueError(
            f"Unsupported provider: {provider_name}"
        )
