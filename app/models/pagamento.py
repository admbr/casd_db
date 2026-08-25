from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field
from pydantic import field_validator


class PagamentoBase(SQLModel):
    customer_id: str
    billingtype: str
    value: float
    duedate: date
    id_asaas: Optional[str] = Field(default=None)
    deleted: Optional[bool] = Field(default=None)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    clientpaymentdate: Optional[date] = Field(default=None)
    datecreated: Optional[date] = Field(default=None)
    invoicenumber: Optional[int] = Field(default=None)
    invoiceurl: Optional[str] = Field(default=None)
    netvalue: Optional[float] = Field(default=None)
    originalduedate: Optional[date] = Field(default=None)
    paymentdate: Optional[date] = Field(default=None)
    apartamento_id: Optional[int] = Field(default=None)

    @field_validator("billingtype", mode="before")
    @classmethod
    def adjust_billing_type(cls, value: str | None) -> str:
        if value != "BOLEOT" and value != "PIX" and value != "CREDIT_CARD":
            return "UNDEFINED"
        return value


class PagamentoRead(PagamentoBase):
    id: int


class PagamentoCreate(PagamentoBase):
    pass


class Pagamentos_asaas(PagamentoBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
