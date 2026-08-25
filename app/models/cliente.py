from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class ClienteBase(SQLModel):
    name: str
    deleted: bool
    datecreated: date
    notificationdisabled: bool
    idcliente: str = Field(unique=True)
    email: Optional[str]
    id_morador: Optional[int]
    cpfcnpj: Optional[str] = Field(index=True)


class ClienteRead(ClienteBase):
    id: int


class ClienteCreate(ClienteBase):
    pass


class Clientes(ClienteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
