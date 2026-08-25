from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field
from pydantic import BaseModel


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
    customer_id: str


class CartaoRead(CartaoBase):
    id: int


class CartaoCreate(CartaoBase):
    pass


class Cartoes(CartaoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
