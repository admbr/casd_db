import pandas as pd
import streamlit as st

from api import clientes as clientes_api
from api.client import ApiError
from components.sidebar import render_sidebar
from components.theme import inject_css
from components.ui import empty_state, show_api_error
from config import settings

st.set_page_config(page_title=f"Clientes · {settings.APP_TITLE}", page_icon="💼", layout="wide")
inject_css()
render_sidebar()

st.title("💼 Clientes")
st.caption("Clientes vinculados à cobrança (Asaas).")

tab_list, tab_id, tab_cpf, tab_new, tab_del, tab_sync = st.tabs(
    ["📋 Listar", "🔍 Buscar por ID", "🔍 Buscar por CPF", "➕ Cadastrar / Vincular", "🗑️ Excluir", "🔁 Sincronizar"]
)

with tab_list:
    col1, col2, col3 = st.columns([1, 1, 2])
    offset = col1.number_input("Offset", min_value=0, value=0, step=10, key="cli_offset")
    limit = col2.number_input("Limite", min_value=1, max_value=500, value=50, step=10, key="cli_limit")
    if col3.button("🔄 Atualizar lista", key="cli_refresh"):
        st.session_state.pop("clientes_data", None)

    if "clientes_data" not in st.session_state:
        try:
            st.session_state["clientes_data"] = clientes_api.list_clientes(
                offset=int(offset), limit=int(limit)
            )
        except ApiError as err:
            show_api_error(err)
            st.session_state["clientes_data"] = []

    data = st.session_state.get("clientes_data") or []
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        st.caption(f"{len(data)} cliente(s) exibido(s).")
    else:
        empty_state("Nenhum cliente encontrado para os parâmetros informados.")

with tab_id:
    cliente_id = st.number_input("ID do cliente", min_value=1, step=1, key="cli_search_id")
    if st.button("Buscar", key="cli_search_id_btn"):
        try:
            result = clientes_api.get_cliente_by_id(int(cliente_id))
            if result:
                st.dataframe(pd.DataFrame([result]), use_container_width=True, hide_index=True)
            else:
                empty_state("Cliente não encontrado.")
        except ApiError as err:
            show_api_error(err)

with tab_cpf:
    cpf = st.text_input("CPF", key="cli_search_cpf")
    if st.button("Buscar", key="cli_search_cpf_btn"):
        if not cpf:
            st.warning("Informe um CPF.")
        else:
            try:
                result = clientes_api.get_cliente_by_cpf(cpf)
                if result:
                    st.dataframe(pd.DataFrame([result]), use_container_width=True, hide_index=True)
                else:
                    empty_state("Cliente não encontrado.")
            except ApiError as err:
                show_api_error(err)

with tab_new:
    st.caption("Cria o cliente localmente (e no Asaas, se ainda não existir um com o mesmo CPF).")
    with st.form("novo_cliente_form"):
        nome = st.text_input("Nome *")
        cpf_novo = st.text_input("CPF *")
        submitted = st.form_submit_button("Cadastrar / Vincular cliente")
        if submitted:
            if not nome or not cpf_novo:
                st.warning("Preencha nome e CPF.")
            else:
                try:
                    created = clientes_api.get_or_create_cliente(nome=nome, cpf=cpf_novo)
                    st.success(f"Cliente '{created.get('name', nome)}' pronto (id {created.get('id')}).")
                    st.session_state.pop("clientes_data", None)
                except ApiError as err:
                    show_api_error(err)

with tab_del:
    st.caption("Remove um cliente pelo ID.")
    del_id = st.number_input("ID do cliente a excluir", min_value=1, step=1, key="cli_del_id")
    confirm = st.checkbox("Confirmo que desejo excluir este cliente.", key="cli_del_confirm")
    if st.button("🗑️ Excluir cliente", key="cli_del_btn", disabled=not confirm):
        try:
            clientes_api.delete_cliente(int(del_id))
            st.success(f"Cliente {int(del_id)} excluído.")
            st.session_state.pop("clientes_data", None)
        except ApiError as err:
            show_api_error(err)

with tab_sync:
    st.caption("Sincroniza os dados de clientes e cobranças com o Asaas.")
    if st.button("🔁 Sincronizar clientes com Asaas", key="cli_sync_btn"):
        with st.spinner("Sincronizando..."):
            try:
                result = clientes_api.sync_clientes()
                st.success("Sincronização concluída.")
                if result:
                    st.json(result)
                st.session_state.pop("clientes_data", None)
            except ApiError as err:
                show_api_error(err)
