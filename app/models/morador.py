from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class MoradorBase(SQLModel):
    nome: str = Field()
    apelido: Optional[str] = None
    id_apartamento: int = Field(foreign_key="apartamentos.id")
    cpf: str = Field(unique=True, index=True)
    turma: str
    celular: Optional[str]
    email: Optional[str]
    admin: int = Field(default=0)
    inscrito: bool = Field(default=False)


class MoradorRead(MoradorBase):
    id: int


class MoradorCreate(MoradorBase):
    senha: Optional[str]


class Moradores(MoradorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    owner: Optional["Apartamentos"] = Relationship(back_populates="moradores")  # type: ignore
