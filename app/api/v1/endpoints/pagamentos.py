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


@router.get("/", response_model=list[PagamentoRead])
async def read_pagamentos(
    offset: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Pagamentos_asaas).offset(offset).limit(limit)
    results = await session.execute(statement)
    return results.scalars().all()


@router.put("/")
async def update_pagamentos(
    billing_service: BillingService = Depends(get_billing_service),
):
    return await billing_service.update_pagamentos()


@router.post("/", response_model=PagamentoRead)
async def crete_payment(
    customer_id: str,
    value: float,
    due_date: date,
    billing_type: str,
    description: Optional[str] = None,
    apartamento_id: Optional[int] = None,
    billing_service: BillingService = Depends(get_billing_service),
    session: AsyncSession = Depends(get_session),
):
    return await billing_service.create_payment(
        PagamentoCreate(
            customer_id=customer_id,
            billingtype=billing_type,
            value=value,
            duedate=due_date,
            description=description,
            apartamento_id=apartamento_id,
        )
    )


@router.delete("/")
async def delete_payment(
    id: str,
    billing_service: BillingService = Depends(get_billing_service),
):
    return await billing_service.delete_payment_by_id(id=id)
