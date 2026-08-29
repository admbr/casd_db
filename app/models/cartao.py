from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.models.cliente import Clientes


class CardInfo(BaseModel):
    holderName: str
    number: str
    expiryMonth: str
    expiryYear: str
    ccv: str


class CardHolderInfo(BaseModel):
    name: str
    email: str
    cpfCnpj: str
    postalCode: str
    addressNumber: str
    phone: str


class CartaoBase(SQLModel):
    token: str = Field(unique=True, index=True)
    brand: str
    last_digits: str
    customer_id: str = Field(foreign_key="clientes.cliente_id")


class CartaoRead(CartaoBase):
    id: int


class CartaoCreate(CartaoBase):
    pass


class Cartoes(CartaoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    dono: Optional["Clientes"] = Relationship(back_populates="cartoes")
