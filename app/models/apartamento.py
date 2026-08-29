from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class ApartamentoBase(SQLModel):
    bloco: str
    numero: str


class ApartamentoRead(ApartamentoBase):
    id: int


class ApartamentoCreate(ApartamentoBase):
    pass


class Apartamentos(ApartamentoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    habitantes: list["Moradores"] = Relationship(back_populates="moradia")  # type: ignore
