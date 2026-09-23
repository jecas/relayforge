import asyncio
from typing import Annotated

from fastapi import FastAPI, Form, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="RelayForge Mock Provider",
)


class AuthorizationRequest(BaseModel):
    login_hint: str
    client_id: str


class AlphaVerificationRequest(BaseModel):
    phone_number: str


class BetaVerificationRequest(BaseModel):
    phone: str


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
    }


@app.post("/oauth/authorize")
async def authorize(
    request: AuthorizationRequest,
) -> dict[str, str]:
    if request.login_hint.endswith("500"):
        raise HTTPException(
            status_code=503,
            detail="Provider unavailable",
        )

    if request.login_hint.endswith("429"):
        raise HTTPException(
            status_code=429,
            detail="Rate limited",
            headers={
                "Retry-After": "1",
            },
        )

    if request.login_hint.endswith("999"):
        await asyncio.sleep(10)

    return {
        "auth_req_id": "mock-auth-request",
    }


@app.post("/oauth/token")
async def token(
    auth_req_id: Annotated[str, Form()],
    client_id: Annotated[str, Form()],
    client_secret: Annotated[str, Form()],
) -> dict[str, str]:
    if (
        auth_req_id != "mock-auth-request"
        or client_id != "relayforge"
        or client_secret != "development-secret"
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    return {
        "access_token": "mock-access-token",
        "token_type": "Bearer",
    }


@app.post("/verify")
async def verify_alpha(
    request: AlphaVerificationRequest,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, bool | int]:
    if authorization != "Bearer mock-access-token":
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    return {
        "match": True,
        "risk_score": 18,
    }


@app.post("/beta/verify")
async def verify_beta(
    request: BetaVerificationRequest,
    x_api_key: Annotated[
        str | None,
        Header(alias="X-API-Key"),
    ] = None,
) -> dict[str, bool | int]:
    if x_api_key != "development-beta-key":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
        )

    return {
        "valid": True,
        "confidence": 91,
    }
