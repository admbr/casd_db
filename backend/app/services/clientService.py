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
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import text, select
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any


class ClientService:
    def __init__(self, asaas_client: AsaasClient, db_session: AsyncSession):
        self.asaas_client = asaas_client
        self.db_session = db_session

    async def fetch_clients_from_asaas(self) -> list[ClienteCreate]:
        return await self.asaas_client.list_all_customers()

    async def fetch_client_by_id(self, id: int) -> ClienteRead:
        statement = select(Clientes).where(Clientes.id == id)

        # Use session.exec() with await, then .first()
        result = await self.db_session.execute(statement)
        cliente = result.scalars().first()

        # Handle missing record
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )

        return ClienteRead(**cliente.model_dump())

    async def fetch_client_by_cpf(self, cpf: str) -> ClienteRead:
        statement = select(Clientes).where(Clientes.cpf_cnpj == cpf)

        # Use session.exec() with await, then .first()
        result = await self.db_session.execute(statement)
        cliente = result.scalars().first()

        # Handle missing record
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )

        return ClienteRead(**cliente.model_dump())

    async def update_clients(self) -> dict[str, Any]:
        clients = await self.fetch_clients_from_asaas()

        if not clients:
            return {"synced": 0, "status": "ok"}

        rows = [client.model_dump() for client in clients]

        statement = pg_insert(Clientes).values(rows)
        update_cols = {
            col: statement.excluded[col]
            for col in rows[0].keys()
            if col not in ("client_id", "morador_id")
        }

        statement = statement.on_conflict_do_update(
            index_elements=["cliente_id"],
            set_=update_cols,
        )

        await self.db_session.execute(statement)
        await self.db_session.commit()

        return {"synced": len(clients), "status": "ok"}

    async def get_or_create_client(self, name: str, cpf: str) -> Clientes:
        response = await self.asaas_client.get_or_create_customer(
            nome=name,
            cpf_cnpj=cpf,
        )
        statement = select(Clientes).where(Clientes.cliente_id == response["id"])
        cliente = (await self.db_session.execute(statement)).scalars().first()
        if cliente:
            return cliente

        cliente = Clientes.model_validate(
            {
                "name": response["name"],
                "deleted": response["deleted"],
                "date_created": response["dateCreated"],
                "notification_disabled": response["notificationDisabled"],
                "cliente_id": response["id"],
                "email": response["email"],
                "morador_id": None,
                "cpf_cnpj": response["cpfCnpj"],
            }
        )

        self.db_session.add(cliente)
        await self.db_session.commit()
        await self.db_session.refresh(cliente)

        return cliente

    async def delete_client_by_id(self, id: int) -> dict[str, Any]:
        return await self.asaas_client.del_client_by_id(
            (await self.fetch_client_by_id(id)).cliente_id
        )
