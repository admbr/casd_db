"""Calls to the /pagamentos endpoints exposed by the backend."""

from typing import Any, Optional

from api.client import delete, get, post, put


def get_pagamento_by_id(pagamento_id: int) -> Any:
    return get("/pagamentos/", {"id": pagamento_id})


def list_pagamentos(offset: int = 0, limit: int = 100) -> Any:
    return get("/pagamentos/intervalo", {"offset": offset, "limit": limit})


def create_pagamento(
    customer_id: str,
    value: float,
    due_date: str,
    billing_type: str,
    description: Optional[str] = None,
    apartamento_id: Optional[int] = None,
) -> Any:
    return post(
        "/pagamentos/",
        {
            "customer_id": customer_id,
            "value": value,
            "due_date": due_date,
            "billing_type": billing_type,
            "description": description,
            "apartamento_id": apartamento_id,
        },
    )


def delete_pagamento(pagamento_id: str) -> Any:
    return delete("/pagamentos/", {"id": pagamento_id})


def sync_pagamentos() -> Any:
    """Triggers the backend's payment status sync with Asaas."""
    return put("/pagamentos/update_all")
