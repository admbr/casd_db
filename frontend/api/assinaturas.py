"""Calls to the /assinaturas endpoints exposed by the backend.

Note: the backend currently only exposes creation of subscriptions —
there is no list/get-by-id endpoint yet, so the frontend can't offer
those views until the backend adds them.
"""

from typing import Any

from api.client import post


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
