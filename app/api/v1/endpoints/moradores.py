from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any
from app.src.database import get_session
from app.models.morador import Moradores, MoradorCreate, MoradorRead

router = APIRouter()


@router.get("/", response_model=MoradorRead)
async def read_moradores_by_id(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Moradores).where(Moradores.id == id)
    results = await session.execute(statement)
    return results.scalars().first()


@router.post("/")
async def create_morador(
    nome: str,
    apartamento_id: int,
    cpf: str,
    turma: str,
    celular: Optional[str] = None,
    email: Optional[str] = None,
    admin: int = 0,
    inscrito: bool = False,
    apelido: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
):
    new_morador = Moradores(
        nome=nome,
        apartamento_id=apartamento_id,
        cpf=cpf,
        turma=turma,
        celular=celular,
        email=email,
        admin=admin,
        inscrito=inscrito,
        apelido=apelido,
        senha="-",
    )

    session.add(Moradores(**new_morador.model_dump()))
    await session.commit()
    await session.refresh(new_morador)

    return new_morador


@router.get("/intervalo", response_model=list[MoradorRead])
async def read_moradores(
    offset: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Moradores).offset(offset).limit(limit)
    results = await session.execute(statement)
    return results.scalars().all()
