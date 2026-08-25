from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class AssinaturaBase(SQLModel):
    id_customer: str
    billing_type: str
    value: float
    next_due_date: str
    cycle: str
    description: Optional[str]
    status: Optional[str]
    id_asaas: Optional[str] = Field(unique=True, index=True, default_factory=None)


class AssinaturaRead(AssinaturaBase):
    id: int


class AssinaturaCreate(AssinaturaBase):
    pass


class Assinaturas(AssinaturaBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
