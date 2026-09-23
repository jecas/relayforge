from uuid import uuid4

from fastapi import APIRouter, Depends, Header

from app.api.dependencies import get_verification_service
from app.schemas.verification import (
    VerificationRequest,
    VerificationResponse,
)
from app.services.verification import VerificationService

router = APIRouter(
    prefix="/verifications",
    tags=["verifications"],
)


@router.post(
    "",
    response_model=VerificationResponse,
)
async def create_verification(
    request: VerificationRequest,
    service: VerificationService = Depends(
        get_verification_service
    ),
    x_correlation_id: str | None = Header(
        default=None,
        alias="X-Correlation-ID",
    ),
) -> VerificationResponse:
    correlation_id = x_correlation_id or str(uuid4())

    result = await service.verify(
        phone_number=request.phone_number,
        correlation_id=correlation_id,
    )

    return VerificationResponse(
        correlation_id=correlation_id,
        result=result,
    )
