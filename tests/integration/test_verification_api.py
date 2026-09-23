from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.dependencies import get_verification_service
from app.core.exceptions import ProviderUnavailableError
from app.main import app
from app.schemas.verification import VerificationResult


def test_create_verification() -> None:
    service = AsyncMock()

    service.verify.return_value = VerificationResult(
        verified=True,
        risk_level="low",
        provider="alpha",
    )

    app.dependency_overrides[
        get_verification_service
    ] = lambda: service

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/verifications",
                json={
                    "phone_number": "+381641234567",
                },
                headers={
                    "X-Correlation-ID": "corr-api-123",
                },
            )

        assert response.status_code == 200

        assert response.json() == {
            "correlation_id": "corr-api-123",
            "result": {
                "verified": True,
                "risk_level": "low",
                "provider": "alpha",
            },
        }

        service.verify.assert_awaited_once_with(
            phone_number="+381641234567",
            correlation_id="corr-api-123",
        )

    finally:
        app.dependency_overrides.clear()

def test_generates_correlation_id_when_missing() -> None:
    service = AsyncMock()

    service.verify.return_value = VerificationResult(
        verified=False,
        risk_level="medium",
        provider="alpha",
    )

    app.dependency_overrides[
        get_verification_service
    ] = lambda: service

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/verifications",
                json={
                    "phone_number": "+381641234567",
                },
            )

        assert response.status_code == 200

        body = response.json()

        assert body["correlation_id"]
        assert body["result"]["verified"] is False
        assert body["result"]["risk_level"] == "medium"

        call = service.verify.await_args

        generated_correlation_id = call.kwargs[
            "correlation_id"
        ]

        assert generated_correlation_id
        assert (
            generated_correlation_id
            == body["correlation_id"]
        )

    finally:
        app.dependency_overrides.clear()

def test_provider_unavailable_returns_normalized_error() -> None:
    service = AsyncMock()

    service.verify.side_effect = ProviderUnavailableError()

    app.dependency_overrides[
        get_verification_service
    ] = lambda: service

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/verifications",
                json={
                    "phone_number": "+381641234567",
                },
                headers={
                    "X-Correlation-ID": "corr-error-123",
                },
            )

        assert response.status_code == 503

        assert response.json() == {
            "correlation_id": "corr-error-123",
            "error": {
                "code": "provider_unavailable",
                "message": (
                    "The provider is temporarily unavailable."
                ),
            },
        }

    finally:
        app.dependency_overrides.clear()
