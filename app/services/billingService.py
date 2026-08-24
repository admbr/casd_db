from pydantic import BaseModel, Field
from app.models.pagamento import (
    Pagamentos_asaas,
    PagamentoRead,
    PagamentoBase,
    PagamentoCreate,
)
from app.src.asaas import AsaasClient
from typing import Any


class BillingService(BaseModel):
    asaas_client: AsaasClient

    async def fetch_all_payments_from_asaas(self) -> list[PagamentoCreate]:
        return await self.asaas_client.list_all_payments()

    async def delete_payment_by_id(self, id: str) -> dict[str, Any]:
        return await self.asaas_client.del_payment_by_id(id)
