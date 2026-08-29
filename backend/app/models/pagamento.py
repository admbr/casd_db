from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator

if TYPE_CHECKING:
    from app.models.cliente import Clientes


class PagamentoBase(SQLModel):
    value: float
    description: Optional[str] = Field(default=None)
    billing_type: str
    due_date: date
    customer_id: str = Field(foreign_key="clientes.cliente_id")
    asaas_id: Optional[str] = Field(default=None, unique=True)
    deleted: Optional[bool] = Field(default=None)
    status: Optional[str] = Field(default=None)
    client_payment_date: Optional[date] = Field(default=None)
    invoice_number: Optional[int] = Field(default=None)
    invoice_url: Optional[str] = Field(default=None)
    net_value: Optional[float] = Field(default=None)
    original_duedate: Optional[date] = Field(default=None)
    payment_date: Optional[date] = Field(default=None)
    bank_slip_url: Optional[str] = Field(default=None)
    date_created: Optional[str] = Field(default=None)
    original_due_date: Optional[str] = Field(default=None)

    @field_validator("billing_type", mode="before")
    @classmethod
    def adjust_billing_type(cls, value: str | None) -> str:
        if value not in ("BOLETO", "PIX", "CREDIT_CARD"):
            return "UNDEFINED"
        return value


class PagamentoRead(PagamentoBase):
    id: int


class PagamentoCreate(PagamentoBase):
    pass


class Pagamentos_asaas(PagamentoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    titular: Optional["Clientes"] = Relationship(back_populates="dividas")
