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


@router.put("/")
async def update_pagamentos(
    billing_service: BillingService = Depends(get_billing_service),
    session: AsyncSession = Depends(get_session),
):
    payments = await billing_service.fetch_all_payments_from_asaas()

    await session.execute(
        text("TRUNCATE TABLE pagamentos_asaas RESTART IDENTITY CASCADE;")
    )

    result = await session.execute(text("SELECT idcliente FROM clientes"))
    valid_ids = {row[0] for row in result.all()}
    valid_payments = []
    skipped = []
    for payment in payments:
        data = payment.model_dump()
        if data["customer_id"] not in valid_ids:
            skipped.append(data["customer_id"])
            continue
        valid_payments.append(data)

    session.add_all([Pagamentos_asaas(**payment) for payment in valid_payments])

    await session.commit()

    return {
        "synced": len(payments),
        "status": "ok",
        "skipped": len(skipped),
        "skipped_customer_ids": list(set(skipped)),
    }
