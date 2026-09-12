from jinja2 import Environment, FileSystemLoader, select_autoescape
import smtplib
from collections.abc import Callable
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.pagamento import (
    PagamentoBase,
    PagamentoCreate,
    PagamentoRead,
    Pagamentos_asaas,
)
from app.src.config import settings
from app.models.morador import Moradores
from app.models.cliente import Clientes
from sqlmodel import select, col
from fastapi import HTTPException, status
from typing import Any


class NotifyService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def notify_some(
        self,
        payments: list[Pagamentos_asaas],
    ) -> dict[str, Any]:
        response: dict[str, Any] = {"sent": 0, "errors": []}

        if not payments:
            return response

        payment_ids = [p.id for p in payments]
        statement = (
            select(Pagamentos_asaas)
            .where(col(Pagamentos_asaas.id).in_(payment_ids))
            .options(
                selectinload(Pagamentos_asaas.titular).selectinload(Clientes.dono)  # type: ignore[arg-type]
            )
        )
        loaded = (await self.db_session.execute(statement)).scalars().all()

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            try:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(settings.gmail_user, settings.gmail_password)

            except Exception as conn_err:
                response["errors"].append(
                    f"Failed to connect or log into SMTP server: {conn_err}"
                )
                return response

            for payment in loaded:
                emails: list[str] = []
                cliente_titular = payment.titular
                if not cliente_titular:
                    response["errors"].append(
                        f"Client not found for payment {payment.asaas_id}"
                    )
                    continue

                morador_lider = cliente_titular.dono
                if not morador_lider:
                    if not cliente_titular.email:
                        response["errors"].append(
                            f"Unable to find email for client {cliente_titular.cliente_id}"
                        )
                        continue
                    emails.append(cliente_titular.email)
                else:
                    ap_id = morador_lider.apartamento_id
                    statement = select(Moradores.email).where(
                        Moradores.apartamento_id == ap_id
                    )
                    r = await self.db_session.execute(statement)
                    emails.extend(r.scalars().all())

                links = []
                if payment.invoice_url:
                    links.append(f"Fatura: {payment.invoice_url}")
                if payment.bank_slip_url:
                    links.append(f"Boleto: {payment.bank_slip_url}")
                links_text = (
                    "\n".join(links) if links else "Link de pagamento indisponível."
                )

                body = (
                    f"Olá,\n\n"
                    f"Você possui uma cobrança no valor de R$ {payment.value:.2f}, "
                    f"com vencimento em {payment.due_date}.\n\n"
                    f"{links_text}\n\n"
                    f"Atenciosamente,\n{settings.sender_name}"
                )

                for email in emails:
                    try:
                        msg = MIMEMultipart()
                        msg["From"] = f"{settings.sender_name} <{settings.gmail_user}>"
                        msg["To"] = email
                        msg["Subject"] = "Cobrança CASD"
                        msg.attach(MIMEText(body, "plain"))
                        server.sendmail(
                            settings.gmail_user,
                            str(email),
                            msg.as_string(),
                        )
                        response["sent"] += 1
                    except Exception as e:
                        response["errors"].append(
                            f"Error sending email to {email}: {e}"
                        )

        return response
