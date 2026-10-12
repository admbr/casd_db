from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_, col
from app.models.morador import MoradorBase, MoradorCreate, Moradores, MoradorRead
from typing import Sequence, Optional
from fastapi import HTTPException, status


class MoradorService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search_morador(self, q: str, limit: int = 20) -> Sequence[Moradores]:
        if len(q.strip()) < 2:
            return []
        term = f"%{q.strip()}%"
        statement = (
            select(Moradores)
            .where(
                or_(
                    col(Moradores.nome).ilike(term),
                    col(Moradores.cpf).ilike(term),
                )
            )
            .limit(limit)
        )
        results = await self.db_session.execute(statement)
        return results.scalars().all()

    async def read_morador_by_id(self, id: int) -> Moradores:
        statement = select(Moradores).where(Moradores.id == id)
        result = await self.db_session.execute(statement)
        morador = result.scalars().first()
        if not morador:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Morador not found",
            )
        return morador

    async def create_morador(
        self,
        nome: str,
        apartamento_id: int,
        cpf: str,
        turma: str,
        celular: Optional[str] = None,
        email: Optional[str] = None,
        admin: int = 0,
        inscrito: bool = False,
        apelido: Optional[str] = None,
    ):
        new_morador = Moradores(
            nome=nome,
            apartamento_id=apartamento_id,
            cpf=cpf,
            turma=turma,
            celular=celular,
            email=email,
            admin=admin,
            inscrito=inscrito,
            apelido=apelido,
            senha="-",
        )

        self.db_session.add(new_morador)
        await self.db_session.commit()
        await self.db_session.refresh(new_morador)

        return new_morador

    async def read_moradores(self) -> Sequence[Moradores]:
        statement = select(Moradores)
        result = await self.db_session.execute(statement)
        return result.scalars().all()
