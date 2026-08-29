from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.cliente import Clientes


class AssinaturaBase(SQLModel):
    customer_id: str = Field(foreign_key="clientes.cliente_id")
    billing_type: str
    value: float
    next_due_date: str
    cycle: str
    description: Optional[str]
    status: Optional[str]
    asaas_id: Optional[str] = Field(unique=True, index=True, default_factory=None)


class AssinaturaRead(AssinaturaBase):
    id: int


class AssinaturaCreate(AssinaturaBase):
    pass


class Assinaturas(AssinaturaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    assinante: Optional["Clientes"] = Relationship(back_populates="planos")
