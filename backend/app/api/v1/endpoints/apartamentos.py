from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.api.v1.deps import get_session
from app.models.apartamento import Apartamentos, ApartamentoRead

router = APIRouter()


@router.get("/", response_model=list[ApartamentoRead])
async def list_apartamentos(session: AsyncSession = Depends(get_session)):
    statement = select(Apartamentos).order_by(Apartamentos.bloco, Apartamentos.numero)
    return (await session.execute(statement)).scalars().all()
