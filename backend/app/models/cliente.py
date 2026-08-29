from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.morador import Moradores
    from app.models.pagamento import Pagamentos_asaas
    from app.models.cartao import Cartoes
    from app.models.assinatura import Assinaturas


class ClienteBase(SQLModel):
    name: str
    deleted: bool
    date_created: date
    notification_disabled: bool
    cliente_id: str = Field(unique=True)
    email: Optional[str]
    morador_id: Optional[int] = Field(foreign_key="moradores.id")
    cpf_cnpj: Optional[str] = Field(index=True)


class ClienteRead(ClienteBase):
    id: int


class ClienteCreate(ClienteBase):
    pass


class Clientes(ClienteBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    dono: Optional["Moradores"] = Relationship(back_populates="contas")
    dividas: list["Pagamentos_asaas"] = Relationship(back_populates="titular")
    cartoes: list["Cartoes"] = Relationship(back_populates="dono")
    planos: list["Assinaturas"] = Relationship(back_populates="assinante")
