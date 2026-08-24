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


class ClientService(BaseModel):
    asaas_client: AsaasClient

    async def fetch_clients_from_asaas(self) -> list[ClienteCreate]:
        return await self.asaas_client.list_all_customers()
