from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.dependencies import get_verification_service
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
