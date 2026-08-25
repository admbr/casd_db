from pydantic import BaseModel, Field
from app.models.pagamento import (
    Pagamentos_asaas,
    PagamentoRead,
    PagamentoCreate,
)
from app.src.asaas import AsaasClient
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, text


class BillingService:
    def __init__(
        self,
        asaas_client: AsaasClient,
        db_session: AsyncSession,
    ):
        self.asaas_client = asaas_client
        self.db_session = db_session

    async def fetch_all_payments_from_asaas(self) -> list[PagamentoCreate]:
        return await self.asaas_client.list_all_payments()

    async def delete_payment_by_id(self, id: str) -> dict[str, Any]:
        return await self.asaas_client.del_payment_by_id(id)

    async def create_payment(
        self,
        payment_in: PagamentoCreate,
    ) -> Pagamentos_asaas:
        payment = Pagamentos_asaas.model_validate(
            await self.asaas_client.create_payment(
                payment_in=payment_in,
            )
        )

        self.db_session.add(payment)
        await self.db_session.commit()
        await self.db_session.refresh(payment)

        return payment

    async def update_pagamentos(self) -> dict[str, Any]:
        payments = await self.fetch_all_payments_from_asaas()

        await self.db_session.execute(
            text("TRUNCATE TABLE pagamentos_asaas RESTART IDENTITY CASCADE;")
        )

        result = await self.db_session.execute(text("SELECT idcliente FROM clientes"))
        valid_ids = {row[0] for row in result.all()}
        valid_payments = []
        skipped = []
        for payment in payments:
            data = payment.model_dump()
            if data["customer_id"] not in valid_ids:
                skipped.append(data["customer_id"])
                continue
            valid_payments.append(data)

        self.db_session.add_all(
            [Pagamentos_asaas(**payment) for payment in valid_payments]
        )

        await self.db_session.commit()

        return {
            "synced": len(payments),
            "status": "ok",
            "skipped": len(skipped),
            "skipped_customer_ids": list(set(skipped)),
        }
