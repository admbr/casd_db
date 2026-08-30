"""Calls to the /cartoes endpoints exposed by the backend."""

from typing import Any, Optional

from api.client import get


def list_cartoes(customer_id: Optional[str] = None) -> Any:
    return get("/cartoes/", {"customer_id": customer_id})
