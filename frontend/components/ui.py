"""Small reusable UI helpers shared across pages."""

import streamlit as st

from api.client import ApiError
from components.theme import COLORS

_STATUS_COLORS = {
    "CONFIRMED": COLORS["success"],
    "RECEIVED": COLORS["success"],
    "RECEIVED_IN_CASH": COLORS["success"],
    "PENDING": COLORS["yellow"],
    "OVERDUE": COLORS["danger"],
    "REFUNDED": COLORS["text_muted"],
    "DELETED": COLORS["text_muted"],
}


def status_badge(status: str | None) -> str:
    """Returns an HTML pill for a Pagamento/Assinatura status string."""
    label = status or "DESCONHECIDO"
    color = _STATUS_COLORS.get(label.upper(), COLORS["text_muted"])
    return (
        f'<span class="casd-badge" '
        f'style="background-color:{color}22;color:{color};border:1px solid {color};">'
        f"{label}</span>"
    )


def show_api_error(err: ApiError) -> None:
    st.error(f"⚠️ {err.message}")


def empty_state(message: str, icon: str = "🗒️") -> None:
    st.info(f"{icon} {message}")
