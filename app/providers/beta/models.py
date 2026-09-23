from pydantic import BaseModel


class BetaVerificationResponse(BaseModel):
    valid: bool
    confidence: int
