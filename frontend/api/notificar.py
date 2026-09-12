"""Calls to the /notificar endpoint exposed by the backend."""

from typing import Any

from api.client import post_json


def notify_payments(payment_ids: list[int]) -> Any:
    return post_json("/notificar/", {"payments_id": payment_ids})
