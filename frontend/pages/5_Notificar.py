import pandas as pd
import streamlit as st

from api import notificar as notificar_api
from api import pagamentos as pagamentos_api
from api.client import ApiError
from components.sidebar import render_sidebar
from components.theme import inject_css
from components.ui import empty_state, show_api_error
from config import settings

st.set_page_config(
    page_title=f"Notificar · {settings.APP_TITLE}", page_icon="🔔", layout="wide"
)
inject_css()
render_sidebar()

st.title("🔔 Notificar cobranças")
st.caption("Envia notificação (e-mail) aos clientes referente a cobranças específicas.")

if "notif_data" not in st.session_state:
    try:
        batch = pagamentos_api.list_pagamentos(offset=0, limit=500)
    except ApiError as err:
        show_api_error(err)
        batch = []
    st.session_state["notif_data"] = [
        p for p in batch if (p.get("status") or "").upper() in ("PENDING", "OVERDUE")
    ]

pendentes = st.session_state.get("notif_data") or []

if not pendentes:
    empty_state("Nenhuma cobrança pendente ou vencida no momento.")
else:
    df = pd.DataFrame(pendentes)

    # --- filtros ---
    col1, col2 = st.columns(2)

    responsaveis = sorted(df["responsavel"].dropna().unique().tolist())
    filtro_responsavel = col1.multiselect(
        "Responsável", options=responsaveis, key="notif_filtro_responsavel"
    )

    apartamentos = sorted(df["apartamento"].dropna().unique().tolist())
    filtro_apartamento = col2.multiselect(
        "Apartamento (numero - bloco)",
        options=apartamentos,
        key="notif_filtro_apartamento",
    )

    if filtro_responsavel:
        df = df[df["responsavel"].isin(filtro_responsavel)]
    if filtro_apartamento:
        df = df[df["apartamento"].isin(filtro_apartamento)]

    df = df[
        [
            "id",
            "customer_id",
            "responsavel",
            "apartamento",
            "value",
            "due_date",
            "status",
            "description",
        ]
    ]
    df.insert(0, "Notificar", False)

    edited = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        disabled=[
            "id",
            "customer_id",
            "responsavel",
            "apartamento",
            "value",
            "due_date",
            "status",
            "description",
        ],
        column_config={"Notificar": st.column_config.CheckboxColumn(required=True)},
        key="notif_editor",
    )

    selecionados = edited[edited["Notificar"]]

    if len(selecionados) > 0:
        st.info(
            f"Você está prestes a notificar **{len(selecionados)}** cobrança(s), "
            f"totalizando **R$ {selecionados['value'].sum():.2f}**."
        )

    if st.button("🔔 Notificar selecionadas", disabled=len(selecionados) == 0):
        ids = selecionados["id"].astype(int).tolist()
        try:
            with st.spinner("Enviando notificações..."):
                result = notificar_api.notify_payments(ids)
            st.success(f"Notificação disparada para {len(ids)} cobrança(s).")
            if result:
                st.json(result)
            st.session_state.pop("notif_data", None)
        except ApiError as err:
            show_api_error(err)

if st.button("🔄 Atualizar lista de pendências"):
    st.session_state.pop("notif_data", None)
    st.rerun()
