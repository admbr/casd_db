from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.database import get_session
from app.models.pagamento import Pagamentos_asaas, PagamentoCreate, PagamentoRead
from app.services.billingService import BillingService
from app.api.v1.deps import get_billing_service
from datetime import date
from typing import Optional
from app.models.assinatura import (
    Assinaturas,
    AssinaturaRead,
    AssinaturaCreate,
    AssinaturaBase,
)

router = APIRouter()


@router.post("/", response_model=AssinaturaRead)
async def create_subscription(
    customer_id: str,
    value: float,
    cycle: str,
    next_due_date: date,
    token: str,
    request: Request,
    description: str,
    billing_service: BillingService = Depends(get_billing_service),
):
    if not request.client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="request.client is falsy"
        )
    return await billing_service.create_subscription(
        customer_id=customer_id,
        credit_card_token=token,
        value=value,
        cycle=cycle,
        next_due_date=next_due_date.isoformat(),
        description=description,
        remote_ip=request.client.host,
    )
