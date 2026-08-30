import pandas as pd
import streamlit as st

from api import clientes as clientes_api
from api.client import ApiError
from components.selectors import select_cliente
from components.sidebar import render_sidebar
from components.theme import inject_css
from components.ui import empty_state, show_api_error
from config import settings

st.set_page_config(
    page_title=f"Clientes · {settings.APP_TITLE}", page_icon="💼", layout="wide"
)
inject_css()
render_sidebar()

st.title("💼 Clientes")
st.caption("Clientes vinculados à cobrança (Asaas).")

# Was 6 tabs (Listar / Buscar por ID / Buscar por CPF / Cadastrar / Excluir / Sincronizar).
# "Buscar por ID" and "Buscar por CPF" collapse into one real search box.
tab_list, tab_search, tab_new, tab_del, tab_sync = st.tabs(
    [
        "📋 Listar",
        "🔍 Buscar",
        "➕ Cadastrar / Vincular",
        "🗑️ Excluir",
        "🔁 Sincronizar",
    ]
)

with tab_list:
    col1, col2, col3 = st.columns([1, 1, 2])
    offset = col1.number_input(
        "Offset", min_value=0, value=0, step=10, key="cli_offset"
    )
    limit = col2.number_input(
        "Limite", min_value=1, max_value=500, value=50, step=10, key="cli_limit"
    )
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

with tab_search:
    # Was two tabs, each asking for a value the admin had to already have
    # in hand (a raw id, or an exact CPF). One search box now covers both,
    # matching on name OR CPF server-side.
    cliente = select_cliente(label="Buscar por nome ou CPF", key="cli_search")
    if cliente:
        st.dataframe(pd.DataFrame([cliente]), use_container_width=True, hide_index=True)

with tab_new:
    st.caption(
        "Cria o cliente localmente (e no Asaas, se ainda não existir um com o mesmo CPF)."
    )
    with st.form("novo_cliente_form"):
        nome = st.text_input("Nome *")
        cpf_novo = st.text_input("CPF *")
        submitted = st.form_submit_button("Cadastrar / Vincular cliente")
        if submitted:
            if not nome or not cpf_novo:
                st.warning("Preencha nome e CPF.")
            else:
                try:
                    created = clientes_api.get_or_create_cliente(
                        nome=nome, cpf=cpf_novo
                    )
                    st.success(f"Cliente '{created.get('name', nome)}' pronto.")
                    st.session_state.pop("clientes_data", None)
                except ApiError as err:
                    show_api_error(err)

with tab_del:
    # Was: st.number_input("ID do cliente a excluir") — a bare integer,
    # confirmed against a generic "Confirmo que desejo excluir este
    # cliente." message with no way to double check *who* that id was.
    st.caption(
        "Busque o cliente e confirme a exclusão pelo nome, não pelo número interno."
    )
    cliente = select_cliente(label="Cliente a excluir (nome ou CPF)", key="cli_del")

    if cliente:
        st.warning(
            f"Você está prestes a excluir **{cliente['name']}** "
            f"(CPF {cliente.get('cpf_cnpj') or 'não informado'})."
        )
        confirm = st.checkbox(
            f"Confirmo que desejo excluir {cliente['name']}.", key="cli_del_confirm"
        )
        if st.button("🗑️ Excluir cliente", key="cli_del_btn", disabled=not confirm):
            try:
                clientes_api.delete_cliente(int(cliente["id"]))
                st.success(f"Cliente '{cliente['name']}' excluído.")
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
