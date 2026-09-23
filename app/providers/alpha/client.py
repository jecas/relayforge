import httpx
from pydantic import ValidationError

from app.core.exceptions import (
    ProviderProtocolError,
    ProviderTimeoutError,
)
from app.providers.alpha.models import (
    AlphaVerificationResponse,
    AuthorizationResponse,
    TokenResponse,
)
from app.providers.error_mapper import map_provider_response_error
from app.providers.retry import with_retry
from app.schemas.verification import VerificationResult


class AlphaProvider:
    name = "alpha"

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        client_id: str,
        client_secret: str,
        max_attempts: int = 3,
        retry_base_delay_seconds: float = 0.25,
    ) -> None:
        self._http_client = http_client
        self._client_id = client_id
        self._client_secret = client_secret
        self._max_attempts = max_attempts
        self._retry_base_delay_seconds = retry_base_delay_seconds

    async def verify(
        self,
        phone_number: str,
        correlation_id: str,
    ) -> VerificationResult:
        return await with_retry(
            lambda: self._execute_flow(
                phone_number=phone_number,
                correlation_id=correlation_id,
            ),
            max_attempts=self._max_attempts,
            base_delay_seconds=self._retry_base_delay_seconds,
            provider_name=self.name,
        )

    async def _execute_flow(
        self,
        phone_number: str,
        correlation_id: str,
    ) -> VerificationResult:
        try:
            auth_req_id = await self._authorize(
                phone_number=phone_number,
                correlation_id=correlation_id,
            )

            access_token = await self._fetch_token(
                auth_req_id=auth_req_id,
                correlation_id=correlation_id,
            )

            provider_response = await self._verify_phone(
                phone_number=phone_number,
                access_token=access_token,
                correlation_id=correlation_id,
            )

            return self._normalize(provider_response)

        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError() from exc

        except ValidationError as exc:
            raise ProviderProtocolError() from exc

    async def _authorize(
        self,
        phone_number: str,
        correlation_id: str,
    ) -> str:
        response = await self._http_client.post(
            "/oauth/authorize",
            json={
                "login_hint": phone_number,
                "client_id": self._client_id,
            },
            headers={
                "X-Correlation-ID": correlation_id,
            },
        )

        self._raise_for_provider_error(response)

        parsed = AuthorizationResponse.model_validate(
            response.json()
        )

        return parsed.auth_req_id

    async def _fetch_token(
        self,
        auth_req_id: str,
        correlation_id: str,
    ) -> str:
        response = await self._http_client.post(
            "/oauth/token",
            data={
                "auth_req_id": auth_req_id,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            headers={
                "X-Correlation-ID": correlation_id,
            },
        )

        self._raise_for_provider_error(response)

        parsed = TokenResponse.model_validate(
            response.json()
        )

        return parsed.access_token

    async def _verify_phone(
        self,
        phone_number: str,
        access_token: str,
        correlation_id: str,
    ) -> AlphaVerificationResponse:
        response = await self._http_client.post(
            "/verify",
            json={
                "phone_number": phone_number,
            },
            headers={
                "Authorization": f"Bearer {access_token}",
                "X-Correlation-ID": correlation_id,
            },
        )

        self._raise_for_provider_error(response)

        return AlphaVerificationResponse.model_validate(
            response.json()
        )

    @staticmethod
    def _raise_for_provider_error(
        response: httpx.Response,
    ) -> None:
        if response.is_error:
            raise map_provider_response_error(response)

    def _normalize(
        self,
        response: AlphaVerificationResponse,
    ) -> VerificationResult:
        if response.risk_score < 30:
            risk_level = "low"
        elif response.risk_score < 70:
            risk_level = "medium"
        else:
            risk_level = "high"

        return VerificationResult(
            verified=response.match,
            risk_level=risk_level,
            provider=self.name,
        )
