import streamlit as st

from components.sidebar import render_sidebar
from components.theme import inject_css
from config import settings

st.set_page_config(
    page_title=f"{settings.APP_TITLE} · Painel",
    page_icon="🟡",
    layout="wide",
)

inject_css()
render_sidebar()

st.title("Painel CASD")
st.caption("Gestão de moradores, clientes, pagamentos e assinaturas.")

st.markdown("### Módulos disponíveis")

CARDS = [
    ("👥", "Moradores", "Consultar e cadastrar moradores dos apartamentos.", "pages/1_Moradores.py"),
    ("💼", "Clientes", "Consultar, cadastrar, sincronizar e remover clientes Asaas.", "pages/2_Clientes.py"),
    ("💳", "Pagamentos", "Consultar, criar, sincronizar e remover cobranças.", "pages/3_Pagamentos.py"),
    ("📄", "Assinaturas", "Criar novas assinaturas recorrentes.", "pages/4_Assinaturas.py"),
    ("🔔", "Notificar", "Disparar notificações de cobranças pendentes.", "pages/5_Notificar.py"),
]

cols = st.columns(2)
for i, (icon, name, desc, target) in enumerate(CARDS):
    with cols[i % 2]:
        st.markdown(
            f"""
            <div class="casd-card">
                <div class="casd-card-icon">{icon}</div>
                <div class="casd-card-title">{name}</div>
                <div class="casd-card-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        try:
            st.page_link(target, label=f"Abrir {name}", icon=icon)
        except Exception:
            st.caption(f"Acesse **{name}** pelo menu lateral.")

with st.expander("⚙️ Configuração da API"):
    st.write(
        "Este painel consome a API FastAPI do backend. Para apontar para "
        "outro endereço, defina a variável de ambiente `API_BASE_URL` "
        "(ou crie um arquivo `.env` a partir de `.env.example`) antes de "
        "iniciar o Streamlit."
    )
    st.code(f"API_BASE_URL={settings.API_BASE_URL}", language="bash")
