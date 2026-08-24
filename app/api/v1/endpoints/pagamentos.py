from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.database import get_session
from app.models.pagamento import Pagamentos_asaas, PagamentoCreate, PagamentoRead
from app.services.billingService import BillingService
from app.api.v1.deps import get_billing_service

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


@router.post("/")
async def update_pagamentos(
    billing_service: BillingService = Depends(get_billing_service),
    session: AsyncSession = Depends(get_session),
):
    payments = await billing_service.fetch_all_payments_from_asaas()

    await session.execute(text("TRUNCATE TABLE item RESTART IDENTITY CASCADE;"))

    session.add_all([Pagamentos_asaas(**payment.model_dump()) for payment in payments])

    await session.commit()

    return {"synced": len(payments), "status": "ok"}
