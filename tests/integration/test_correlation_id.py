from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app


def test_preserves_client_correlation_id() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={
                "X-Correlation-ID": "corr-client-123",
            },
        )

    assert response.status_code == 200

    assert (
        response.headers["X-Correlation-ID"]
        == "corr-client-123"
    )


def test_generates_correlation_id_when_missing() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200

    correlation_id = response.headers[
        "X-Correlation-ID"
    ]

    UUID(correlation_id)
