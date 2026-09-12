from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pagamento import (
    PagamentoBase,
    PagamentoCreate,
    PagamentoRead,
    Pagamentos_asaas,
)
from typing import Any
from app.services.notifyService import NotifyService
from app.services.billingService import BillingService
from app.api.v1.deps import get_notify_service
from app.api.v1.deps import get_billing_service
from app.src.database import get_session
from pydantic import BaseModel

router = APIRouter()


class NotifyRequest(BaseModel):
    payments_id: list[int]


@router.post("/")
async def notify_payments(
    payload: NotifyRequest,
    billing_service: BillingService = Depends(get_billing_service),
    notify_service: NotifyService = Depends(get_notify_service),
) -> dict[str, Any]:
    result: dict[str, Any] = {"id_errors": []}
    payments = []
    for payment_id in payload.payments_id:
        try:
            payment = await billing_service.get_payment_by_id(payment_id)
            payments.append(payment)
        except HTTPException:
            result["id_errors"].append(f"Error for payment id: {payment_id}")

    notify_result = await notify_service.notify_some(payments=payments)
    result["sent"] = notify_result.get("sent", 0)
    result["errors"] = notify_result.get("errors", [])
    return result
