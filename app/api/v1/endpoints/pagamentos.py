from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.database import get_session
from app.models.pagamento import Pagamentos_asaas, PagamentoCreate, PagamentoRead
from app.services.billingService import BillingService
from app.api.v1.deps import get_billing_service
from datetime import date
from typing import Optional

router = APIRouter()


@router.get("/", response_model=PagamentoRead)
async def read_payment_by_id(
    id: int, billing_service: BillingService = Depends(get_billing_service)
):
    return await billing_service.get_payment_by_id(id=id)


@router.post("/", response_model=PagamentoRead)
async def create_payment(
    customer_id: str,
    value: float,
    due_date: date,
    billing_type: str,
    description: Optional[str] = None,
    apartamento_id: Optional[int] = None,
    billing_service: BillingService = Depends(get_billing_service),
):
    return await billing_service.create_payment(
        PagamentoCreate(
            customer_id=customer_id,
            billing_type=billing_type,
            value=value,
            due_date=due_date,
            description=description,
        )
    )


@router.delete("/")
async def delete_payment(
    id: str,
    billing_service: BillingService = Depends(get_billing_service),
):
    return await billing_service.delete_payment_by_id(id=id)


@router.get("/intervalo", response_model=list[PagamentoRead])
async def read_pagamentos(
    offset: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Pagamentos_asaas).offset(offset).limit(limit)
    results = await session.execute(statement)
    return results.scalars().all()


@router.get("/apartamento/", response_model=list[PagamentoRead])
async def read_pagamentos_from_ap_id():
    return


@router.put("/update_all")
async def update_pagamentos(
    billing_service: BillingService = Depends(get_billing_service),
):
    return await billing_service.update_pagamentos()
