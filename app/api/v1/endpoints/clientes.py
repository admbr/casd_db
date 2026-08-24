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


@router.put("/")
async def update_pagamentos(
    billing_service: ClientService = Depends(get_client_service),
    session: AsyncSession = Depends(get_session),
):
    clients = await billing_service.fetch_clients_from_asaas()

    await session.execute(text("TRUNCATE TABLE clientes RESTART IDENTITY CASCADE;"))

    session.add_all([Clientes(**client.model_dump()) for client in clients])

    await session.commit()

    return {"synced": len(clients), "status": "ok"}
