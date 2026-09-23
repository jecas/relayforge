import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.core.context import get_correlation_id


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }

        for field in (
            "event",
            "provider",
            "operation",
            "attempt",
            "max_attempts",
            "status_code",
            "retry_delay_seconds",
        ):
            value = getattr(record, field, None)

            if value is not None:
                payload[field] = value

        return json.dumps(
            payload,
            default=str,
        )


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
