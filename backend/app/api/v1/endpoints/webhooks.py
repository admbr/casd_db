from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.api.v1.deps import get_billing_service
from app.services.billingService import BillingService
from app.src.config import settings

router = APIRouter()


@router.post("/asaas")
async def receive_asaas_webhook(
    request: Request,
    billing_service: BillingService = Depends(get_billing_service),
):
    if settings.asaas_webhook_token:
        token = request.headers.get("asaas-access-token")
        if token != settings.asaas_webhook_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook token",
            )

    payload = await request.json()
    return await billing_service.process_asaas_webhook(payload)
