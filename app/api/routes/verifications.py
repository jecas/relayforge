from fastapi import APIRouter, Depends, Request

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
    request_body: VerificationRequest,
    request: Request,
    service: VerificationService = Depends(
        get_verification_service
    ),
) -> VerificationResponse:
    correlation_id = request.state.correlation_id

    result = await service.verify(
        phone_number=request_body.phone_number,
        correlation_id=correlation_id,
        provider_name=request_body.provider,
    )

    return VerificationResponse(
        correlation_id=correlation_id,
        result=result,
    )
