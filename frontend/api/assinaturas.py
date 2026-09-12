"""Calls to the /assinaturas endpoints exposed by the backend.

Note: the backend currently only exposes creation of subscriptions —
there is no list/get-by-id endpoint yet, so the frontend can't offer
those views until the backend adds them.
"""

from typing import Any, Optional

from api.client import delete, get, post


def list_assinaturas(customer_id: Optional[str] = None) -> Any:
    return get("/assinaturas/", {"customer_id": customer_id})


def get_assinatura(id: int) -> Any:
    return get(f"/assinaturas/{id}")


def cancel_assinatura(id: int) -> Any:
    return delete(f"/assinaturas/{id}")


def create_assinatura(
    customer_id: str,
    value: float,
    cycle: str,
    next_due_date: str,
    token: str,
    description: str,
) -> Any:
    return post(
        "/assinaturas/",
        {
            "customer_id": customer_id,
            "value": value,
            "cycle": cycle,
            "next_due_date": next_due_date,
            "token": token,
            "description": description,
        },
    )
