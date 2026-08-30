from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, or_, col
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any
from app.src.database import get_session
from app.models.morador import Moradores, MoradorCreate, MoradorRead

router = APIRouter()


@router.get("/buscar", response_model=list[MoradorRead])
async def search_moradores(
    q: str,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    if len(q.strip()) < 2:
        return []
    term = f"%{q.strip()}%"
    statement = (
        select(Moradores)
        .where(or_(col(Moradores.nome).ilike(term), col(Moradores.cpf).ilike(term)))
        .limit(limit)
    )
    results = await session.execute(statement)
    return results.scalars().all()


@router.get("/", response_model=MoradorRead)
async def read_moradores_by_id(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Moradores).where(Moradores.id == id)
    results = await session.execute(statement)
    morador = results.scalars().first()
    if not morador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Morador not found",
        )
    return morador


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

    session.add(new_morador)
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
