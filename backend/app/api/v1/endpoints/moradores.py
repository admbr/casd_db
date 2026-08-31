from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, or_, col
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any
from app.src.database import get_session
from app.models.morador import Moradores, MoradorCreate, MoradorRead
from app.services.moradorService import MoradorService
from app.api.v1.deps import get_morador_service

router = APIRouter()


@router.get("/buscar", response_model=list[MoradorRead])
async def search_moradores(
    q: str,
    limit: int = 20,
    morador_service: MoradorService = Depends(get_morador_service),
):
    return await morador_service.search_morador(q=q, limit=limit)


@router.get("/", response_model=MoradorRead)
async def read_moradores_by_id(
    id: int, morador_service: MoradorService = Depends(get_morador_service)
):
    return await morador_service.read_morador_by_id(id=id)


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
    morador_service: MoradorService = Depends(get_morador_service),
):
    return await morador_service.create_morador(
        nome=nome,
        apartamento_id=apartamento_id,
        cpf=cpf,
        turma=turma,
        celular=celular,
        email=email,
        admin=admin,
        inscrito=inscrito,
        apelido=apelido,
    )


@router.get("/intervalo", response_model=list[MoradorRead])
async def read_moradores(
    morador_service: MoradorService = Depends(get_morador_service),
):
    return await morador_service.read_moradores()
