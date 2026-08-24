from typing import Optional
from datetime import date
from sqlmodel import SQLModel, Field


class ClienteBase(SQLModel):
    deleted: bool
    email: Optional[str]
    id_morador: Optional[int]
    name: str
    cpfcnpj: Optional[str] = Field(index=True)
    datecreated: date
    notificationdisabled: bool
    idcliente: str = Field(unique=True)


class ClienteRead(ClienteBase):
    id: int


class ClienteCreate(ClienteBase):
    pass


class Clientes(ClienteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
