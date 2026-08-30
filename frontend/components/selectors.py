"""
Shared search-and-select widgets.

Every page that needs to reference a morador, apartamento, cliente, or
cartao does it through one of these instead of a raw st.number_input /
st.text_input for an ID. Centralizing it here means the lookup logic
(and its caching) only has to be gotten right once.
"""

from typing import Any, Optional

import streamlit as st

from api import apartamentos as apartamentos_api
from api import cartoes as cartoes_api
from api import clientes as clientes_api
from api import moradores as moradores_api
from api.client import ApiError


def select_apartamento(
    label: str = "Apartamento", key: str = "apto_select"
) -> Optional[int]:
    """Returns the chosen apartamento_id, or None if nothing's picked yet."""
    if "_apartamentos_cache" not in st.session_state:
        try:
            st.session_state["_apartamentos_cache"] = (
                apartamentos_api.list_apartamentos()
            )
        except ApiError as err:
            st.warning(f"Não foi possível carregar apartamentos: {err.message}")
            st.session_state["_apartamentos_cache"] = []

    apartamentos = st.session_state["_apartamentos_cache"]
    if not apartamentos:
        st.caption("Nenhum apartamento cadastrado ainda.")
        return None

    options = {
        f"Bloco {a['bloco']} · Apto {a['numero']}": a["id"] for a in apartamentos
    }
    choice = st.selectbox(label, options=list(options.keys()), key=key)
    return options.get(choice)


def _search_and_pick(
    label: str,
    search_fn,
    format_fn,
    id_field: str,
    key: str,
    help_text: str = "Digite ao menos 2 caracteres",
) -> Optional[Any]:
    """Generic 'type to search, pick from matches' pattern."""
    query = st.text_input(label, key=f"{key}_query", help=help_text)

    if not query or len(query.strip()) < 2:
        return None

    try:
        matches = search_fn(query.strip())
    except ApiError as err:
        st.warning(f"Busca falhou: {err.message}")
        return None

    if not matches:
        st.caption("Nenhum resultado encontrado.")
        return None

    options = {format_fn(m): m for m in matches}
    choice = st.selectbox("Selecione", options=list(options.keys()), key=f"{key}_pick")
    return options.get(choice)


def select_cliente(
    label: str = "Cliente (nome ou CPF)", key: str = "cli_select"
) -> Optional[dict]:
    """Returns the full cliente dict chosen, or None."""
    return _search_and_pick(
        label=label,
        search_fn=clientes_api.search_clientes,
        format_fn=lambda c: f"{c['name']} · CPF {c.get('cpf_cnpj') or 'não informado'}",
        id_field="cliente_id",
        key=key,
    )


def select_morador(
    label: str = "Morador (nome ou CPF)", key: str = "mor_select"
) -> Optional[dict]:
    """Returns the full morador dict chosen, or None."""
    return _search_and_pick(
        label=label,
        search_fn=moradores_api.search_moradores,
        format_fn=lambda m: f"{m['nome']} · {m.get('apelido') or 'sem apelido'}",
        id_field="id",
        key=key,
    )


def select_cartao(
    customer_id: str, label: str = "Cartão salvo", key: str = "cartao_select"
) -> Optional[str]:
    """
    Returns the chosen card's token, given an already-resolved customer_id.
    Depends on select_cliente() (or equivalent) having run first.
    """
    cache_key = f"_cartoes_cache_{customer_id}"
    if cache_key not in st.session_state:
        try:
            st.session_state[cache_key] = cartoes_api.list_cartoes(
                customer_id=customer_id
            )
        except ApiError as err:
            st.warning(f"Não foi possível carregar cartões: {err.message}")
            st.session_state[cache_key] = []

    cartoes = st.session_state[cache_key]
    if not cartoes:
        st.caption("Este cliente ainda não tem cartão salvo.")
        return None

    options = {f"•••• {c['last_digits']} ({c['brand']})": c["token"] for c in cartoes}
    choice = st.selectbox(label, options=list(options.keys()), key=key)
    return options.get(choice)
