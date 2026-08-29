"""Calls to the /notificar endpoint exposed by the backend."""

from typing import Any

from api.client import post


def notify_payments(payment_ids: list[int]) -> Any:
    return post("/notificar/", {"payments_id": payment_ids})
