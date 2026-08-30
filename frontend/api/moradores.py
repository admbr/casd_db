"""Calls to the /moradores endpoints exposed by the backend."""

from typing import Any, Optional

from api.client import get, post


def get_morador_by_id(morador_id: int) -> Any:
    return get("/moradores/", {"id": morador_id})


def search_moradores(query: str) -> Any:
    return get("/moradores/buscar", {"q": query})


def list_moradores(offset: int = 0, limit: int = 100) -> Any:
    return get("/moradores/intervalo", {"offset": offset, "limit": limit})


def create_morador(
    nome: str,
    apartamento_id: int,
    cpf: str,
    turma: str,
    celular: Optional[str] = None,
    email: Optional[str] = None,
    admin: int = 0,
    inscrito: bool = False,
    apelido: Optional[str] = None,
) -> Any:
    return post(
        "/moradores/",
        {
            "nome": nome,
            "apartamento_id": apartamento_id,
            "cpf": cpf,
            "turma": turma,
            "celular": celular,
            "email": email,
            "admin": admin,
            "inscrito": inscrito,
            "apelido": apelido,
        },
    )
