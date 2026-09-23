import subprocess
import sys


def run_query(query: str) -> str:
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "postgres",
            "psql",
            "-U",
            "relayforge",
            "-d",
            "relayforge",
            "-t",
            "-A",
            "-c",
            query,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def verify_record(
    correlation_id: str,
    expected_provider: str,
) -> None:
    result = run_query(
        f"""
        SELECT provider || ':' || status || ':' || risk_level
        FROM verification_audits
        WHERE correlation_id = '{correlation_id}';
        """
    )

    expected = (
        f"{expected_provider}:success:low"
    )

    assert result == expected, (
        f"Unexpected audit record for "
        f"{correlation_id}: {result!r}"
    )

    print(
        f"Audit record verified: "
        f"{correlation_id}"
    )


def main() -> None:
    verify_record(
        correlation_id="e2e-alpha-123",
        expected_provider="alpha",
    )

    verify_record(
        correlation_id="e2e-beta-123",
        expected_provider="beta",
    )

    print(
        "All audit records verified."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(
            f"Audit verification failed: {exc}",
            file=sys.stderr,
        )
        raise
