from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class PagamentoBase(SQLModel):
    customer_id: str = Field(unique=True)
    id_asaas: str
    deleted: bool
    description: Optional[str]
    value: float
    status: str
    clientpaymentdate: Optional[date]
    datecreated: date
    duedate: date
    invoicenumber: int
    invoiceurl: str
    netvalue: float
    originalduedate: date
    paymentdate: Optional[date]
    billingtype: str


class PagamentoRead(PagamentoBase):
    id: int


class PagamentoCreate(PagamentoBase):
    pass


class Pagamentos_asaas(PagamentoBase, table=True):
    id: int
