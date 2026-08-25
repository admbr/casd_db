from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.database import get_session
from app.models.cliente import Clientes, ClienteRead, ClienteCreate, ClienteBase
from app.services.clientService import ClientService
from app.api.v1.deps import get_client_service

router = APIRouter()


@router.get("/", response_model=list[ClienteRead])
async def read_clients(
    offset: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Clientes).offset(offset).limit(limit)
    results = await session.execute(statement)
    return results.scalars().all()


@router.get("/", response_model=ClienteRead)
async def read_client_by_cpf(
    cpf: str,
    client_service: ClientService = Depends(get_client_service),
):
    return await client_service.fetch_client_by_cpf(cpf=cpf)


@router.put("/")
async def update_clients(
    client_service: ClientService = Depends(get_client_service),
):
    return await client_service.update_clients()


@router.post("/", response_model=ClienteRead)
async def get_or_create_client(
    nome: str, cpf: str, client_service: ClientService = Depends(get_client_service)
):
    return await client_service.get_or_create_client(name=nome, cpf=cpf)
