from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import health, verifications
from app.core.config import get_settings
from app.core.exceptions import RelayForgeError

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Resilient asynchronous API integration "
        "service for external providers."
    ),
)


@app.exception_handler(RelayForgeError)
async def relayforge_error_handler(
    request: Request,
    exc: RelayForgeError,
) -> JSONResponse:
    correlation_id = request.headers.get(
        "X-Correlation-ID"
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
