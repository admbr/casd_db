from datetime import date, timedelta

import streamlit as st

from api import assinaturas as assinaturas_api
from api import cartoes as cartoes_api
from api.client import ApiError
from components.sidebar import render_sidebar
from components.selectors import select_cartao, select_cliente
from components.theme import inject_css
from components.ui import empty_state, show_api_error, status_badge
from config import settings

st.set_page_config(
    page_title=f"Assinaturas · {settings.APP_TITLE}", page_icon="📄", layout="wide"
)
inject_css()
render_sidebar()

st.title("📄 Assinaturas")
st.caption("Cria e gerencia cobranças recorrentes no cartão de crédito.")

CYCLES = ["WEEKLY", "BIWEEKLY", "MONTHLY", "QUARTERLY", "SEMIANNUALLY", "YEARLY"]

st.subheader("Nova assinatura")

cliente = select_cliente(key="assinatura_cliente")

if cliente is None:
    empty_state("Selecione um cliente para começar.")
else:
    customer_id = cliente["cliente_id"]

    st.markdown("**Cartão de cobrança**")
    modo_cartao = st.radio(
        "Cartão",
        ["Usar cartão salvo", "Cadastrar novo cartão"],
        horizontal=True,
        key="modo_cartao",
        label_visibility="collapsed",
    )

    token = None

    if modo_cartao == "Usar cartão salvo":
        token = select_cartao(customer_id, key=f"assinatura_cartao_{customer_id}")
    else:
        with st.form("novo_cartao_form"):
            col1, col2 = st.columns(2)
            with col1:
                holder_name = st.text_input(
                    "Nome no cartão", value=cliente.get("name") or ""
                )
                number = st.text_input("Número do cartão")
                ccv = st.text_input("CCV", max_chars=4)
            with col2:
                expiry_month = st.text_input("Mês de expiração (MM)", max_chars=2)
                expiry_year = st.text_input("Ano de expiração (AAAA)", max_chars=4)

            st.markdown("**Dados do titular** (exigidos pela Asaas)")
            col3, col4 = st.columns(2)
            with col3:
                holder_email = st.text_input("E-mail", value=cliente.get("email") or "")
                holder_cpf_cnpj = st.text_input(
                    "CPF/CNPJ", value=cliente.get("cpf_cnpj") or ""
                )
            with col4:
                holder_postal_code = st.text_input("CEP")
                holder_address_number = st.text_input("Número do endereço")
            holder_phone = st.text_input("Telefone")

            tokenizar = st.form_submit_button("💳 Salvar cartão")

            if tokenizar:
                required = [
                    holder_name,
                    number,
                    expiry_month,
                    expiry_year,
                    ccv,
                    holder_email,
                    holder_cpf_cnpj,
                    holder_postal_code,
                    holder_address_number,
                    holder_phone,
                ]
                if not all(required):
                    st.warning("Preencha todos os campos do cartão e do titular.")
                else:
                    try:
                        with st.spinner("Tokenizando cartão com a Asaas..."):
                            novo_cartao = cartoes_api.tokenize_cartao(
                                customer_id=customer_id,
                                holder_name=holder_name,
                                number=number.replace(" ", ""),
                                expiry_month=expiry_month,
                                expiry_year=expiry_year,
                                ccv=ccv,
                                holder_email=holder_email,
                                holder_cpf_cnpj=holder_cpf_cnpj,
                                holder_postal_code=holder_postal_code,
                                holder_address_number=holder_address_number,
                                holder_phone=holder_phone,
                            )
                        st.session_state.pop(f"_cartoes_cache_{customer_id}", None)
                        st.success(
                            f"Cartão •••• {novo_cartao['last_digits']} "
                            f"({novo_cartao['brand']}) salvo com sucesso."
                        )
                        token = novo_cartao["token"]
                        st.session_state[f"_novo_token_{customer_id}"] = token
                    except ApiError as err:
                        show_api_error(err)

        token = st.session_state.get(f"_novo_token_{customer_id}", token)

    st.markdown("---")
    st.markdown("**Detalhes da assinatura**")

    with st.form("nova_assinatura_form"):
        col1, col2 = st.columns(2)
        with col1:
            value = st.number_input(
                "Valor (R$)", min_value=0.01, step=10.0, format="%.2f"
            )
            cycle = st.selectbox(
                "Ciclo de cobrança", CYCLES, index=CYCLES.index("MONTHLY")
            )
        with col2:
            next_due_date = st.date_input(
                "Primeiro vencimento", value=date.today() + timedelta(days=1)
            )
            description = st.text_input("Descrição", placeholder="Ex: Taxa condominial")

        criar = st.form_submit_button("📄 Criar assinatura", disabled=token is None)

        if not token:
            st.caption(
                "Selecione ou cadastre um cartão acima antes de criar a assinatura."
            )

        if criar and token:
            try:
                with st.spinner("Criando assinatura na Asaas..."):
                    assinaturas_api.create_assinatura(
                        customer_id=customer_id,
                        value=value,
                        cycle=cycle,
                        next_due_date=next_due_date.isoformat(),
                        token=token,
                        description=description,
                    )
                st.success("Assinatura criada com sucesso.")
                st.session_state.pop(f"_novo_token_{customer_id}", None)
                st.session_state.pop("_assinaturas_list_cache", None)
                st.rerun()
            except ApiError as err:
                show_api_error(err)

st.markdown("---")
st.subheader("Assinaturas existentes")

col_filtro, col_refresh = st.columns([3, 1])
with col_filtro:
    filtro_customer_id = st.text_input(
        "Filtrar por cliente (customer_id)", value="", key="assinatura_filtro"
    )
with col_refresh:
    st.write("")
    if st.button("🔄 Atualizar"):
        st.session_state.pop("_assinaturas_list_cache", None)

cache_key = f"_assinaturas_list_cache_{filtro_customer_id or 'all'}"
if cache_key not in st.session_state:
    try:
        st.session_state[cache_key] = assinaturas_api.list_assinaturas(
            customer_id=filtro_customer_id or None
        )
    except ApiError as err:
        show_api_error(err)
        st.session_state[cache_key] = []

assinaturas = st.session_state.get(cache_key) or []

if not assinaturas:
    empty_state("Nenhuma assinatura encontrada.")
else:
    for a in assinaturas:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            c1.markdown(f"**{a.get('description') or 'Sem descrição'}**")
            c1.caption(f"Cliente: {a['customer_id']}")
            c2.markdown(f"R$ {a['value']:.2f} · {a['cycle']}")
            c2.caption(f"Próx. vencimento: {a['next_due_date']}")
            c3.markdown(status_badge(a.get("status")), unsafe_allow_html=True)
            c3.caption(f"ID: {a['id']}")
            if a.get("status") != "CANCELLED":
                if c4.button("Cancelar", key=f"cancel_{a['id']}"):
                    try:
                        assinaturas_api.cancel_assinatura(a["id"])
                        st.session_state.pop(cache_key, None)
                        st.success("Assinatura cancelada.")
                        st.rerun()
                    except ApiError as err:
                        show_api_error(err)
