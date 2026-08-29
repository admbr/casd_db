from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.cliente import Clientes
    from app.models.apartamento import Apartamentos


class MoradorBase(SQLModel):
    nome: str
    apelido: Optional[str] = None
    apartamento_id: int = Field(foreign_key="apartamentos.id")
    cpf: Optional[str] = Field(index=True)
    turma: str
    celular: Optional[str]
    email: Optional[str]
    admin: int = Field(default=0)
    inscrito: bool = Field(default=False)
    senha: Optional[str]


class MoradorRead(MoradorBase):
    id: int


class MoradorCreate(MoradorBase):
    pass


class Moradores(MoradorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    moradia: Optional["Apartamentos"] = Relationship(back_populates="habitantes")
    contas: list["Clientes"] = Relationship(back_populates="dono")
