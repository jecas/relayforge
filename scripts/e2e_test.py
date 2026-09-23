import json
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "http://localhost:8000"


def request(
    method: str,
    path: str,
    payload: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, object], dict[str, str]]:
    data = None

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request_headers = {
        "Content-Type": "application/json",
        **(headers or {}),
    }

    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=request_headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(
            req,
            timeout=15,
        ) as response:
            body = json.loads(
                response.read().decode("utf-8")
            )

            return (
                response.status,
                body,
                dict(response.headers),
            )

    except urllib.error.HTTPError as exc:
        body = json.loads(
            exc.read().decode("utf-8")
        )

        return (
            exc.code,
            body,
            dict(exc.headers),
        )


def wait_for_api() -> None:
    for _ in range(30):
        try:
            status, _, _ = request(
                "GET",
                "/health",
            )

            if status == 200:
                print("RelayForge is ready.")
                return

        except (
            urllib.error.URLError,
            TimeoutError,
        ):
            pass

        time.sleep(1)

    raise RuntimeError(
        "RelayForge did not become ready."
    )


def test_alpha() -> None:
    correlation_id = "e2e-alpha-123"

    status, body, headers = request(
        "POST",
        "/api/v1/verifications",
        payload={
            "phone_number": "+381641234567",
            "provider": "alpha",
        },
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )

    assert status == 200, body

    assert body == {
        "correlation_id": correlation_id,
        "result": {
            "verified": True,
            "risk_level": "low",
            "provider": "alpha",
        },
    }

    assert (
        headers["X-Correlation-ID"]
        == correlation_id
    )

    print("Alpha E2E passed.")


def test_beta() -> None:
    correlation_id = "e2e-beta-123"

    status, body, headers = request(
        "POST",
        "/api/v1/verifications",
        payload={
            "phone_number": "+381641234567",
            "provider": "beta",
        },
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )

    assert status == 200, body

    assert body == {
        "correlation_id": correlation_id,
        "result": {
            "verified": True,
            "risk_level": "low",
            "provider": "beta",
        },
    }

    assert (
        headers["X-Correlation-ID"]
        == correlation_id
    )

    print("Beta E2E passed.")


def test_provider_unavailable() -> None:
    correlation_id = "e2e-provider-503"

    status, body, headers = request(
        "POST",
        "/api/v1/verifications",
        payload={
            "phone_number": "+38164123500",
            "provider": "alpha",
        },
        headers={
            "X-Correlation-ID": correlation_id,
        },
    )

    assert status == 503, body

    assert body == {
        "correlation_id": correlation_id,
        "error": {
            "code": "provider_unavailable",
            "message": (
                "The provider is temporarily unavailable."
            ),
        },
    }

    assert (
        headers["X-Correlation-ID"]
        == correlation_id
    )

    print("Provider unavailable E2E passed.")


def main() -> None:
    wait_for_api()

    test_alpha()
    test_beta()
    test_provider_unavailable()

    print("All RelayForge E2E tests passed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            f"E2E test failed: {exc}",
            file=sys.stderr,
        )
        raise
