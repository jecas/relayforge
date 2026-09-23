from fastapi import FastAPI

from app.api.routes import health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Resilient asynchronous API integration "
        "service for external providers."
    ),
)

app.include_router(
    health.router
)
