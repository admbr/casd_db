from jinja2 import Environment, FileSystemLoader, select_autoescape
import smtplib
from collections.abc import Callable
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import smtplib
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
from sqlmodel import select
from fastapi import HTTPException, status
from typing import Any


class NotifyService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def notify_some(
        self,
        payments: list[Pagamentos_asaas],
    ) -> dict[str, Any]:
        response = {"sent": 0, "errors": []}

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

            for payment in payments:
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
                    r_emails = r.scalars().all()
                    for email in r_emails:
                        emails.append(email)

                for email in emails:
                    try:
                        subject = f"Cobrança CASD"
                        html = payment.bank_slip_url if payment.bank_slip_url else "-"
                        msg = MIMEMultipart()
                        msg["From"] = f"{settings.sender_name} <{settings.gmail_user}>"
                        msg["To"] = email
                        msg["Subject"] = subject
                        msg.attach(MIMEText(html, "plain"))
                        server.sendmail(
                            settings.gmail_user,
                            str(email),
                            msg.as_string(),
                        )
                    except Exception as e:
                        response["errors"].append(
                            f"Error sending email to {email}: {e}"
                        )

        return response
