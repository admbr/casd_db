from datetime import date
from pydantic import BaseModel, Field
from app.models.pagamento import (
    Pagamentos_asaas,
    PagamentoRead,
    PagamentoCreate,
)
from app.src.asaas import AsaasClient
from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import select, text
from fastapi import Request, HTTPException, status
from app.models.cartao import (
    CartaoBase,
    CartaoCreate,
    CartaoRead,
    Cartoes,
    CardHolderInfo,
    CardInfo,
)
from app.models.assinatura import (
    AssinaturaBase,
    AssinaturaCreate,
    AssinaturaRead,
    Assinaturas,
)


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


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

    async def get_payment_by_id(self, id: int) -> Pagamentos_asaas:
        statement = select(Pagamentos_asaas).where(Pagamentos_asaas.id == id)

        payment = (await self.db_session.execute(statement)).scalars().first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pagamento not found",
            )

        return payment

    async def update_pagamentos(self) -> dict[str, Any]:
        payments = await self.fetch_all_payments_from_asaas()

        result = await self.db_session.execute(text("SELECT cliente_id FROM clientes"))
        valid_ids = {row[0] for row in result.all()}

        valid_payments, skipped = [], []
        for payment in payments:
            data = payment.model_dump()
            if data["customer_id"] not in valid_ids:
                skipped.append(data["customer_id"])
                continue
            valid_payments.append(data)

        if valid_payments:
            stmt = pg_insert(Pagamentos_asaas).values(valid_payments)
            update_cols = {
                col: stmt.excluded[col]
                for col in valid_payments[0].keys()
                if col != "asaas_id"
            }
            stmt = stmt.on_conflict_do_update(
                index_elements=["asaas_id"],
                set_=update_cols,
            )
            await self.db_session.execute(stmt)
            await self.db_session.commit()

        return {
            "synced": len(payments),
            "status": "ok",
            "skipped": len(skipped),
            "skipped_customer_ids": list(set(skipped)),
        }

    async def tokenize_card(
        self,
        customer_id: str,
        card: CardInfo,
        cardholder: CardHolderInfo,
        request: Request,
    ) -> Cartoes:
        if not request.client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"request.client returned falsy",
            )
        result = await self.asaas_client.tokenize_credit_card(
            customer_id=customer_id,
            credit_card=card.model_dump(),
            holder_info=cardholder.model_dump(),
            remote_ip=request.client.host,
        )
        cartao = CartaoCreate(
            token=result["creditCardToken"],
            brand=result["creditCardBrand"],
            customer_id=customer_id,
            last_digits=result["creditCardNumber"],
        )
        try:
            db_cartao = Cartoes(**cartao.model_dump())
            self.db_session.add(db_cartao)
            await self.db_session.commit()
            await self.db_session.refresh(db_cartao)
        except Exception as e:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {e}"
            )
        return db_cartao

    async def create_subscription(
        self,
        customer_id: str,
        value: float,
        next_due_date: str,
        cycle: str,
        description: str,
        credit_card_token: str,
        remote_ip: str,
    ) -> Assinaturas:
        statement = select(Cartoes).where(Cartoes.token == credit_card_token)
        result = await self.db_session.execute(statement)
        cartao = result.scalars().first()

        if not cartao:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card token not found",
            )

        response = await self.asaas_client.create_subscription(
            customer_id=customer_id,
            value=value,
            next_due_date=next_due_date,
            cycle=cycle,
            description=description,
            credit_card_token=cartao.token,
            remote_ip=remote_ip,
        )

        assinatura = Assinaturas(
            asaas_id=response["id"],
            customer_id=customer_id,
            value=value,
            cycle=cycle,
            status=response["status"],
            next_due_date=next_due_date,
            description=description,
            billing_type=response["billingType"],
        )
        self.db_session.add(assinatura)
        await self.db_session.commit()
        await self.db_session.refresh(assinatura)

        return assinatura

    async def list_assinaturas(
        self, customer_id: str | None = None
    ) -> list[Assinaturas]:
        statement = select(Assinaturas)
        if customer_id:
            statement = statement.where(Assinaturas.customer_id == customer_id)
        result = await self.db_session.execute(statement)
        return list(result.scalars().all())

    async def get_assinatura_by_id(self, id: int) -> Assinaturas:
        statement = select(Assinaturas).where(Assinaturas.id == id)
        result = await self.db_session.execute(statement)
        assinatura = result.scalars().first()

        if not assinatura:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assinatura not found"
            )

        return assinatura

    async def cancel_assinatura(self, id: int) -> Assinaturas:
        assinatura = await self.get_assinatura_by_id(id)

        if assinatura.asaas_id:
            await self.asaas_client.cancel_subscription(assinatura.asaas_id)

        assinatura.status = "CANCELLED"
        self.db_session.add(assinatura)
        await self.db_session.commit()
        await self.db_session.refresh(assinatura)

        return assinatura

    async def process_asaas_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = payload.get("event", "")
        payment = payload.get("payment")

        if not event.startswith("PAYMENT_") or not payment:
            return {"handled": False, "reason": "not a payment event"}

        asaas_id = payment.get("id")
        if not asaas_id:
            return {"handled": False, "reason": "missing payment id"}

        statement = select(Pagamentos_asaas).where(
            Pagamentos_asaas.asaas_id == asaas_id
        )
        result = await self.db_session.execute(statement)
        pagamento = result.scalars().first()

        if not pagamento:
            return {"handled": False, "reason": "payment not found locally"}

        pagamento.status = payment.get("status", pagamento.status)
        pagamento.payment_date = (
            _parse_date(payment.get("paymentDate")) or pagamento.payment_date
        )
        pagamento.client_payment_date = (
            _parse_date(payment.get("clientPaymentDate"))
            or pagamento.client_payment_date
        )
        pagamento.net_value = payment.get("netValue", pagamento.net_value)
        pagamento.invoice_url = payment.get("invoiceUrl", pagamento.invoice_url)

        self.db_session.add(pagamento)
        await self.db_session.commit()

        return {"handled": True, "event": event, "asaas_id": asaas_id}
