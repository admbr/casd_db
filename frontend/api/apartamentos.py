"""Calls to the /apartamentos endpoints exposed by the backend."""

from typing import Any

from api.client import get


def list_apartamentos() -> Any:
    return get("/apartamentos/")
