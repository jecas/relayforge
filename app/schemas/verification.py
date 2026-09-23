from typing import Literal

from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):
    phone_number: str = Field(
        min_length=8,
        max_length=20,
        examples=["+381641234567"],
    )

    provider: Literal["alpha", "beta"] = "alpha"


class VerificationResult(BaseModel):
    verified: bool
    risk_level: str
    provider: str


class VerificationResponse(BaseModel):
    correlation_id: str
    result: VerificationResult
