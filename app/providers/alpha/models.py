from pydantic import BaseModel


class AuthorizationResponse(BaseModel):
    auth_req_id: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class AlphaVerificationResponse(BaseModel):
    match: bool
    risk_score: int
