from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.src.database import get_session
from app.models.morador import Moradores, MoradorCreate, MoradorRead

router = APIRouter()


@router.get("/", response_model=list[MoradorRead])
async def read_items(
    offset: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Moradores).offset(offset).limit(limit)
    results = await session.execute(statement)
    return results.scalars().all()
