"""Sidebar branding shown consistently across every page."""

import requests
import streamlit as st

from config import settings


@st.cache_data(ttl=15, show_spinner=False)
def _api_is_healthy() -> bool:
    """Best-effort check that the backend is reachable.

    There's no dedicated /health endpoint, so this just hits the API's
    root and treats anything below a server error as "reachable".
    """
    root_url = settings.API_BASE_URL.split("/api/")[0]
    try:
        response = requests.get(root_url, timeout=3)
        return response.status_code < 500
    except requests.exceptions.RequestException:
        return False


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style="padding:.3rem 0 1rem 0;">
                <span style="font-size:1.6rem;font-weight:800;color:#FFD60A;">CASD</span>
                <span style="font-size:1.6rem;font-weight:800;color:#F5F5F5;"> Painel</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        healthy = _api_is_healthy()
        color = "#4CAF50" if healthy else "#FF5C5C"
        label = "API conectada" if healthy else "API indisponível"
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:.4rem;margin-bottom:.4rem;">
                <span style="height:8px;width:8px;border-radius:50%;
                             background:{color};display:inline-block;"></span>
                <span style="font-size:.8rem;color:#9A9A9E;">{label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(f"`{settings.API_BASE_URL}`")
        st.divider()
