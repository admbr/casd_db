from datetime import date

import pandas as pd
import streamlit as st

from api import pagamentos as pagamentos_api
from api.client import ApiError
from components.sidebar import render_sidebar
from components.theme import inject_css
from components.ui import empty_state, show_api_error, status_badge
from config import settings

st.set_page_config(page_title=f"Pagamentos · {settings.APP_TITLE}", page_icon="💳", layout="wide")
inject_css()
render_sidebar()

st.title("💳 Pagamentos")
st.caption("Cobranças geradas via Asaas.")

BILLING_TYPES = ["BOLETO", "PIX", "CREDIT_CARD"]

tab_list, tab_search, tab_new, tab_del, tab_sync = st.tabs(
    ["📋 Listar", "🔍 Buscar por ID", "➕ Criar cobrança", "🗑️ Excluir", "🔁 Sincronizar"]
)

with tab_list:
    col1, col2, col3 = st.columns([1, 1, 2])
    offset = col1.number_input("Offset", min_value=0, value=0, step=10, key="pag_offset")
    limit = col2.number_input("Limite", min_value=1, max_value=500, value=50, step=10, key="pag_limit")
    if col3.button("🔄 Atualizar lista", key="pag_refresh"):
        st.session_state.pop("pagamentos_data", None)

    if "pagamentos_data" not in st.session_state:
        try:
            st.session_state["pagamentos_data"] = pagamentos_api.list_pagamentos(
                offset=int(offset), limit=int(limit)
            )
        except ApiError as err:
            show_api_error(err)
            st.session_state["pagamentos_data"] = []

    data = st.session_state.get("pagamentos_data") or []
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        st.caption(f"{len(data)} pagamento(s) exibido(s).")
    else:
        empty_state("Nenhum pagamento encontrado para os parâmetros informados.")

with tab_search:
    pagamento_id = st.number_input("ID do pagamento", min_value=1, step=1, key="pag_search_id")
    if st.button("Buscar", key="pag_search_btn"):
        try:
            result = pagamentos_api.get_pagamento_by_id(int(pagamento_id))
            if result:
                st.markdown(status_badge(result.get("status")), unsafe_allow_html=True)
                st.dataframe(pd.DataFrame([result]), use_container_width=True, hide_index=True)
            else:
                empty_state("Pagamento não encontrado.")
        except ApiError as err:
            show_api_error(err)

with tab_new:
    with st.form("novo_pagamento_form"):
        c1, c2 = st.columns(2)
        customer_id = c1.text_input("ID do cliente (Asaas) *")
        billing_type = c2.selectbox("Forma de pagamento *", options=BILLING_TYPES)

        c3, c4 = st.columns(2)
        value = c3.number_input("Valor (R$) *", min_value=0.0, step=10.0, format="%.2f")
        due_date = c4.date_input("Vencimento *", value=date.today())

        c5, c6 = st.columns(2)
        description = c5.text_input("Descrição")
        apartamento_id = c6.number_input("ID do apartamento", min_value=0, step=1, value=0)

        submitted = st.form_submit_button("Criar cobrança")
        if submitted:
            if not customer_id or value <= 0:
                st.warning("Informe o cliente e um valor válido.")
            else:
                try:
                    created = pagamentos_api.create_pagamento(
                        customer_id=customer_id,
                        value=value,
                        due_date=due_date.isoformat(),
                        billing_type=billing_type,
                        description=description or None,
                        apartamento_id=int(apartamento_id) or None,
                    )
                    st.success(f"Cobrança criada (id {created.get('id')}).")
                    st.session_state.pop("pagamentos_data", None)
                except ApiError as err:
                    show_api_error(err)

with tab_del:
    st.caption("Remove uma cobrança pelo ID.")
    del_id = st.text_input("ID do pagamento a excluir", key="pag_del_id")
    confirm = st.checkbox("Confirmo que desejo excluir esta cobrança.", key="pag_del_confirm")
    if st.button("🗑️ Excluir cobrança", key="pag_del_btn", disabled=not confirm):
        if not del_id:
            st.warning("Informe o ID.")
        else:
            try:
                pagamentos_api.delete_pagamento(del_id)
                st.success(f"Cobrança {del_id} excluída.")
                st.session_state.pop("pagamentos_data", None)
            except ApiError as err:
                show_api_error(err)

with tab_sync:
    st.caption("Sincroniza o status das cobranças com o Asaas.")
    if st.button("🔁 Sincronizar pagamentos com Asaas", key="pag_sync_btn"):
        with st.spinner("Sincronizando..."):
            try:
                result = pagamentos_api.sync_pagamentos()
                st.success("Sincronização concluída.")
                if result:
                    st.json(result)
                st.session_state.pop("pagamentos_data", None)
            except ApiError as err:
                show_api_error(err)
