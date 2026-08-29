from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.database import get_session
from app.models.cliente import Clientes, ClienteRead, ClienteCreate, ClienteBase
from app.services.clientService import ClientService
from app.services.billingService import BillingService
from app.api.v1.deps import get_client_service
from app.api.v1.deps import get_billing_service

router = APIRouter()


@router.get("/", response_model=ClienteRead)
async def get_cliente(
    id: int, client_service: ClientService = Depends(get_client_service)
) -> ClienteRead:
    return await client_service.fetch_client_by_id(id=id)


@router.post("/", response_model=ClienteRead)
async def get_or_create_client(
    nome: str, cpf: str, client_service: ClientService = Depends(get_client_service)
):
    return await client_service.get_or_create_client(name=nome, cpf=cpf)


@router.delete("/")
async def delete_cliente(
    id: int, client_service: ClientService = Depends(get_client_service)
):
    return await client_service.delete_client_by_id(id=id)


@router.get("/cpf", response_model=ClienteRead)
async def read_client_by_cpf(
    cpf: str,
    client_service: ClientService = Depends(get_client_service),
):
    return await client_service.fetch_client_by_cpf(cpf=cpf)


@router.put("/update_clientes")
async def update_clients(
    billing_service: BillingService = Depends(get_billing_service),
    client_service: ClientService = Depends(get_client_service),
):
    response = await client_service.update_clients()
    await billing_service.update_pagamentos()
    return response


@router.get("/intervalo", response_model=list[ClienteRead])
async def read_clients(
    offset: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    statement = select(Clientes).offset(offset).limit(limit)
    results = await session.execute(statement)
    return results.scalars().all()
