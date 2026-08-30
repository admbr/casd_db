from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.v1.deps import get_session
from app.models.cartao import CardHolderInfo, CartaoRead, Cartoes
from sqlmodel import select

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
