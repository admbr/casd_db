"""Calls to the /clientes endpoints exposed by the backend."""

from typing import Any

from api.client import delete, get, post, put


def get_cliente_by_id(cliente_id: int) -> Any:
    return get("/clientes/", {"id": cliente_id})


def get_cliente_by_cpf(cpf: str) -> Any:
    return get("/clientes/cpf", {"cpf": cpf})


def list_clientes(offset: int = 0, limit: int = 100) -> Any:
    return get("/clientes/intervalo", {"offset": offset, "limit": limit})


def get_or_create_cliente(nome: str, cpf: str) -> Any:
    return post("/clientes/", {"nome": nome, "cpf": cpf})


def delete_cliente(cliente_id: int) -> Any:
    return delete("/clientes/", {"id": cliente_id})


def sync_clientes() -> Any:
    """Triggers the backend's client + billing sync with Asaas."""
    return put("/clientes/update_clientes")
