from datetime import date

import pandas as pd
import streamlit as st

from api import pagamentos as pagamentos_api
from api.client import ApiError
from components.selectors import select_apartamento, select_cliente
from components.sidebar import render_sidebar
from components.theme import inject_css
from components.ui import empty_state, show_api_error, status_badge
from config import settings

st.set_page_config(
    page_title=f"Pagamentos · {settings.APP_TITLE}", page_icon="💳", layout="wide"
)
inject_css()
render_sidebar()

st.title("💳 Pagamentos")
st.caption("Cobranças geradas via Asaas.")

BILLING_TYPES = ["BOLETO", "PIX", "CREDIT_CARD"]

# Was: Listar / Buscar por ID / Criar cobrança / Excluir / Sincronizar.
# "Buscar por ID" and "Excluir" both required a bare id, and (before the
# backend fix) they were secretly two *different* ids — the local db id
# for search, the Asaas id for delete. They're merged into one
# "cliente -> cobranças desse cliente -> ação" flow instead.
tab_list, tab_cliente, tab_new, tab_sync = st.tabs(
    ["📋 Listar", "🔍 Cobranças por cliente", "➕ Criar cobrança", "🔁 Sincronizar"]
)

with tab_list:
    col1, col2, col3 = st.columns([1, 1, 2])
    offset = col1.number_input(
        "Offset", min_value=0, value=0, step=10, key="pag_offset"
    )
    limit = col2.number_input(
        "Limite", min_value=1, max_value=500, value=50, step=10, key="pag_limit"
    )
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

with tab_cliente:
    cliente = select_cliente(label="Cliente", key="pag_cliente_search")

    if cliente:
        try:
            # TODO backend: add GET /pagamentos/cliente?customer_id= so this
            # doesn't have to pull a batch and filter client-side once the
            # table grows past a page or two.
            batch = pagamentos_api.list_pagamentos(offset=0, limit=500)
        except ApiError as err:
            show_api_error(err)
            batch = []

        pagamentos_cliente = [
            p for p in batch if p.get("customer_id") == cliente["cliente_id"]
        ]

        if not pagamentos_cliente:
            empty_state(f"Nenhuma cobrança encontrada para {cliente['name']}.")
        else:
            st.caption(f"{len(pagamentos_cliente)} cobrança(s) de {cliente['name']}:")
            for pag in pagamentos_cliente:
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                c1.markdown(f"**R$ {pag.get('value', 0):.2f}**")
                c2.markdown(status_badge(pag.get("status")), unsafe_allow_html=True)
                c3.caption(f"Vencimento: {pag.get('due_date', '—')}")
                if c4.button(
                    "🗑️", key=f"pag_del_{pag['id']}", help="Excluir esta cobrança"
                ):
                    st.session_state[f"pag_confirm_{pag['id']}"] = True

                if st.session_state.get(f"pag_confirm_{pag['id']}"):
                    st.warning(
                        f"Confirma excluir a cobrança de R$ {pag.get('value', 0):.2f} "
                        f"de {cliente['name']}, vencimento {pag.get('due_date', '—')}?"
                    )
                    cc1, cc2 = st.columns(2)
                    if cc1.button("Sim, excluir", key=f"pag_del_confirm_{pag['id']}"):
                        try:
                            pagamentos_api.delete_pagamento(int(pag["id"]))
                            st.success("Cobrança excluída.")
                            st.session_state.pop(f"pag_confirm_{pag['id']}", None)
                            st.session_state.pop("pagamentos_data", None)
                            st.rerun()
                        except ApiError as err:
                            show_api_error(err)
                    if cc2.button("Cancelar", key=f"pag_del_cancel_{pag['id']}"):
                        st.session_state.pop(f"pag_confirm_{pag['id']}", None)
                        st.rerun()

with tab_new:
    with st.form("novo_pagamento_form"):
        c1, c2 = st.columns(2)
        with c1:
            # Was: st.text_input("ID do cliente (Asaas)") — a raw string
            # typed from memory, with a typo silently creating a charge
            # against the wrong (or no) customer.
            cliente = select_cliente(label="Cliente *", key="pag_new_cliente")
        billing_type = c2.selectbox("Forma de pagamento *", options=BILLING_TYPES)

        c3, c4 = st.columns(2)
        value = c3.number_input("Valor (R$) *", min_value=0.0, step=10.0, format="%.2f")
        due_date = c4.date_input("Vencimento *", value=date.today())

        c5, c6 = st.columns(2)
        description = c5.text_input("Descrição")
        with c6:
            apartamento_id = select_apartamento(label="Apartamento", key="pag_new_apto")

        submitted = st.form_submit_button("Criar cobrança")
        if submitted:
            if not cliente or value <= 0:
                st.warning("Selecione um cliente e informe um valor válido.")
            else:
                try:
                    created = pagamentos_api.create_pagamento(
                        customer_id=cliente["cliente_id"],
                        value=value,
                        due_date=due_date.isoformat(),
                        billing_type=billing_type,
                        description=description or None,
                        apartamento_id=apartamento_id,
                    )
                    st.success(f"Cobrança criada para {cliente['name']}.")
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
