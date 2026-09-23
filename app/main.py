from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import health, verifications
from app.core.config import get_settings
from app.core.exceptions import RelayForgeError
from app.core.logging import configure_logging
from app.core.middleware import CorrelationIdMiddleware

settings = get_settings()

configure_logging()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Resilient asynchronous API integration "
        "service for external providers."
    ),
)

app.add_middleware(CorrelationIdMiddleware)


@app.exception_handler(RelayForgeError)
async def relayforge_error_handler(
    request: Request,
    exc: RelayForgeError,
) -> JSONResponse:
    correlation_id = getattr(
        request.state,
        "correlation_id",
        None,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "correlation_id": correlation_id,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )


app.include_router(health.router)

app.include_router(
    verifications.router,
    prefix=settings.api_prefix,
)
