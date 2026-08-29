from datetime import date

import streamlit as st

from api import assinaturas as assinaturas_api
from api.client import ApiError
from components.sidebar import render_sidebar
from components.theme import inject_css
from components.ui import show_api_error
from config import settings

st.set_page_config(page_title=f"Assinaturas · {settings.APP_TITLE}", page_icon="📄", layout="wide")
inject_css()
render_sidebar()

st.title("📄 Assinaturas")
st.caption("Cadastro de assinaturas recorrentes (cobrança automática via cartão).")

st.info(
    "A API atualmente disponibiliza apenas a criação de assinaturas — "
    "consulta e listagem ainda não foram implementadas no backend."
)

CYCLES = ["WEEKLY", "BIWEEKLY", "MONTHLY", "QUARTERLY", "SEMIANNUALLY", "YEARLY"]

with st.form("nova_assinatura_form"):
    c1, c2 = st.columns(2)
    customer_id = c1.text_input("ID do cliente (Asaas) *")
    token = c2.text_input("Token do cartão *", help="Token de cartão já tokenizado no Asaas.")

    c3, c4 = st.columns(2)
    value = c3.number_input("Valor (R$) *", min_value=0.0, step=10.0, format="%.2f")
    cycle = c4.selectbox("Ciclo de cobrança *", options=CYCLES, index=2)

    c5, c6 = st.columns(2)
    next_due_date = c5.date_input("Próximo vencimento *", value=date.today())
    description = c6.text_input("Descrição")

    submitted = st.form_submit_button("Criar assinatura")
    if submitted:
        if not customer_id or not token or value <= 0:
            st.warning("Preencha os campos obrigatórios (*).")
        else:
            try:
                created = assinaturas_api.create_assinatura(
                    customer_id=customer_id,
                    value=value,
                    cycle=cycle,
                    next_due_date=next_due_date.isoformat(),
                    token=token,
                    description=description or "",
                )
                st.success(f"Assinatura criada (id {created.get('id')}).")
                st.json(created)
            except ApiError as err:
                show_api_error(err)
