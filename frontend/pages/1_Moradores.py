import pandas as pd
import streamlit as st

from api import moradores as moradores_api
from api.client import ApiError
from components.selectors import select_apartamento, select_morador
from components.sidebar import render_sidebar
from components.theme import inject_css
from components.ui import empty_state, show_api_error
from config import settings

st.set_page_config(
    page_title=f"Moradores · {settings.APP_TITLE}", page_icon="👥", layout="wide"
)
inject_css()
render_sidebar()

st.title("👥 Moradores")
st.caption("Consulte e cadastre moradores vinculados aos apartamentos.")

tab_list, tab_search, tab_new = st.tabs(["📋 Listar", "🔍 Buscar", "➕ Cadastrar"])

with tab_list:
    col1, col2, col3 = st.columns([1, 1, 2])
    offset = col1.number_input(
        "Offset", min_value=0, value=0, step=10, key="mor_offset"
    )
    limit = col2.number_input(
        "Limite", min_value=1, max_value=500, value=50, step=10, key="mor_limit"
    )
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
    # Was: st.number_input("ID do morador") — an admin had to already know
    # the internal id. Now: type a name or CPF, pick from real matches.
    morador = select_morador(label="Buscar morador por nome ou CPF", key="mor_search")
    if morador:
        st.dataframe(pd.DataFrame([morador]), use_container_width=True, hide_index=True)

with tab_new:
    with st.form("novo_morador_form"):
        c1, c2 = st.columns(2)
        nome = c1.text_input("Nome completo *")
        apelido = c2.text_input("Apelido")

        c3, c4 = st.columns(2)
        cpf = c3.text_input("CPF *")
        # Was: st.number_input("ID do apartamento") — the admin had no way
        # to know which integer corresponded to which apartment. Now: a
        # dropdown built from the real apartment list.
        with c4:
            apartamento_id = select_apartamento(
                label="Apartamento *", key="mor_new_apto"
            )

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
                st.warning(
                    "Preencha os campos obrigatórios (*) e selecione um apartamento."
                )
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
                    st.success(
                        f"Morador '{created.get('nome', nome)}' cadastrado com sucesso!"
                    )
                    st.session_state.pop("moradores_data", None)
                except ApiError as err:
                    show_api_error(err)
