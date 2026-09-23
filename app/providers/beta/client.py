import httpx
from pydantic import ValidationError

from app.core.exceptions import (
    ProviderProtocolError,
    ProviderTimeoutError,
)
from app.providers.beta.models import BetaVerificationResponse
from app.providers.error_mapper import map_provider_response_error
from app.providers.retry import with_retry
from app.schemas.verification import VerificationResult


class BetaProvider:
    name = "beta"

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        base_url: str,
        api_key: str,
        max_attempts: int = 3,
        retry_base_delay_seconds: float = 0.25,
    ) -> None:
        self._http_client = http_client
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._max_attempts = max_attempts
        self._retry_base_delay_seconds = retry_base_delay_seconds

    async def verify(
        self,
        phone_number: str,
        correlation_id: str,
    ) -> VerificationResult:
        return await with_retry(
            lambda: self._execute(
                phone_number,
                correlation_id,
            ),
            max_attempts=self._max_attempts,
            base_delay_seconds=self._retry_base_delay_seconds,
            provider_name=self.name,
        )

    async def _execute(
        self,
        phone_number: str,
        correlation_id: str,
    ) -> VerificationResult:
        try:
            response = await self._http_client.post(
                f"{self._base_url}/beta/verify",
                json={
                    "phone": phone_number,
                },
                headers={
                    "X-API-Key": self._api_key,
                    "X-Correlation-ID": correlation_id,
                },
            )

            if response.is_error:
                raise map_provider_response_error(response)

            parsed = BetaVerificationResponse.model_validate(
                response.json()
            )

        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError() from exc

        except ValidationError as exc:
            raise ProviderProtocolError() from exc

        return VerificationResult(
            verified=parsed.valid,
            risk_level=self._risk_level(parsed.confidence),
            provider=self.name,
        )

    @staticmethod
    def _risk_level(confidence: int) -> str:
        if confidence >= 80:
            return "low"

        if confidence >= 50:
            return "medium"

        return "high"
