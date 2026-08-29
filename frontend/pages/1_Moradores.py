import pandas as pd
import streamlit as st

from api import moradores as moradores_api
from api.client import ApiError
from components.sidebar import render_sidebar
from components.theme import inject_css
from components.ui import empty_state, show_api_error
from config import settings

st.set_page_config(page_title=f"Moradores · {settings.APP_TITLE}", page_icon="👥", layout="wide")
inject_css()
render_sidebar()

st.title("👥 Moradores")
st.caption("Consulte e cadastre moradores vinculados aos apartamentos.")

tab_list, tab_search, tab_new = st.tabs(["📋 Listar", "🔍 Buscar por ID", "➕ Cadastrar"])

with tab_list:
    col1, col2, col3 = st.columns([1, 1, 2])
    offset = col1.number_input("Offset", min_value=0, value=0, step=10, key="mor_offset")
    limit = col2.number_input("Limite", min_value=1, max_value=500, value=50, step=10, key="mor_limit")
    if col3.button("🔄 Atualizar lista", key="mor_refresh"):
        st.session_state.pop("moradores_data", None)

    if "moradores_data" not in st.session_state:
        try:
            st.session_state["moradores_data"] = moradores_api.list_moradores(
                offset=int(offset), limit=int(limit)
            )
        except ApiError as err:
            show_api_error(err)
            st.session_state["moradores_data"] = []

    data = st.session_state.get("moradores_data") or []
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        st.caption(f"{len(data)} morador(es) exibido(s).")
    else:
        empty_state("Nenhum morador encontrado para os parâmetros informados.")

with tab_search:
    morador_id = st.number_input("ID do morador", min_value=1, step=1, key="mor_search_id")
    if st.button("Buscar", key="mor_search_btn"):
        try:
            result = moradores_api.get_morador_by_id(int(morador_id))
            if result:
                st.dataframe(pd.DataFrame([result]), use_container_width=True, hide_index=True)
            else:
                empty_state("Morador não encontrado.")
        except ApiError as err:
            show_api_error(err)

with tab_new:
    with st.form("novo_morador_form"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome completo *")
        apelido = c2.text_input("Apelido")

        c3, c4 = st.columns(2)
        cpf = c3.text_input("CPF *")
        apartamento_id = c4.number_input("ID do apartamento *", min_value=1, step=1)

        c5, c6 = st.columns(2)
        turma = c5.text_input("Turma *")
        admin = c6.selectbox("Nível de admin", options=[0, 1, 2], index=0)

        c7, c8 = st.columns(2)
        celular = c7.text_input("Celular")
        email = c8.text_input("E-mail")

        inscrito = st.checkbox("Inscrito", value=False)

        submitted = st.form_submit_button("Cadastrar morador")
        if submitted:
            if not nome or not cpf or not turma or not apartamento_id:
                st.warning("Preencha os campos obrigatórios (*).")
            else:
                try:
                    created = moradores_api.create_morador(
                        nome=nome,
                        apartamento_id=int(apartamento_id),
                        cpf=cpf,
                        turma=turma,
                        celular=celular or None,
                        email=email or None,
                        admin=int(admin),
                        inscrito=inscrito,
                        apelido=apelido or None,
                    )
                    st.success(f"Morador '{created.get('nome', nome)}' cadastrado com sucesso!")
                    st.session_state.pop("moradores_data", None)
                except ApiError as err:
                    show_api_error(err)
