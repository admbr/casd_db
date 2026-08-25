from pydantic import BaseModel, Field
from app.models.morador import MoradorBase, MoradorCreate, Moradores, MoradorRead
from app.models.apartamento import (
    ApartamentoBase,
    ApartamentoCreate,
    ApartamentoRead,
    Apartamentos,
)
from app.models.cliente import ClienteBase, ClienteCreate, ClienteRead, Clientes
from app.src.asaas import AsaasClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import text, select
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any


class ClientService:
    def __init__(self, asaas_client: AsaasClient, db_session: AsyncSession):
        self.asaas_client = asaas_client
        self.db_session = db_session

    async def fetch_clients_from_asaas(self) -> list[ClienteCreate]:
        return await self.asaas_client.list_all_customers()

    async def fetch_client_by_cpf(self, cpf: str) -> Clientes:
        statement = select(Clientes).where(Clientes.cpfcnpj == cpf)

        # Use session.exec() with await, then .first()
        result = await self.db_session.execute(statement)
        cliente = result.scalars().first()

        # Handle missing record
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )

        return cliente

    async def update_clients(self) -> dict[str, Any]:
        clients = await self.fetch_clients_from_asaas()

        await self.db_session.execute(
            text("TRUNCATE TABLE clientes RESTART IDENTITY CASCADE;")
        )

        self.db_session.add_all([Clientes(**client.model_dump()) for client in clients])

        await self.db_session.commit()

        return {"synced": len(clients), "status": "ok"}

    async def get_or_create_client(self, name: str, cpf: str) -> Clientes:
        response = await self.asaas_client.get_or_create_customer(
            nome=name, cpf_cnpj=cpf
        )
        cliente = Clientes(
            name=response["name"],
            deleted=response["deleted"],
            datecreated=response["dateCreated"],
            notificationdisabled=response["notificationDisabled"],
            idcliente=response["id"],
            email=response["email"],
            id_morador=None,
            cpfcnpj=response["cpfCnpj"],
        )

        self.db_session.add(cliente)
        await self.db_session.commit()
        await self.db_session.refresh(cliente)

        return cliente
