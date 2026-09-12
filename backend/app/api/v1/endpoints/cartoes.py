from fastapi import APIRouter, Body, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.v1.deps import get_session
from app.models.cartao import (
    CardHolderInfo,
    CartaoRead,
    Cartoes,
    CardInfo,
    CardHolderInfo,
)
from sqlmodel import select
from app.services.billingService import BillingService
from app.api.v1.deps import get_billing_service

router = APIRouter()


@router.get("/", response_model=list[CartaoRead])
async def list_cartoes(
    customer_id: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Cartoes)
    if customer_id:
        statement = statement.where(Cartoes.customer_id == customer_id)
    return (await session.execute(statement)).scalars().all()


@router.post("/", response_model=CartaoRead)
async def tokenize_cartao(
    request: Request,
    customer_id: str = Body(...),
    card: CardInfo = Body(...),
    card_holder: CardHolderInfo = Body(...),
    billing_service: BillingService = Depends(get_billing_service),
):
    if not request.client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="request.client is falsy"
        )
    return await billing_service.tokenize_card(
        customer_id=customer_id, card=card, cardholder=card_holder, request=request
    )
