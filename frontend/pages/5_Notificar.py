import streamlit as st

from api import notificar as notificar_api
from api.client import ApiError
from components.sidebar import render_sidebar
from components.theme import inject_css
from components.ui import show_api_error
from config import settings

st.set_page_config(page_title=f"Notificar · {settings.APP_TITLE}", page_icon="🔔", layout="wide")
inject_css()
render_sidebar()

st.title("🔔 Notificar cobranças")
st.caption("Envia notificação (e-mail) aos clientes referente a cobranças específicas.")

with st.form("notificar_form"):
    ids_raw = st.text_area(
        "IDs dos pagamentos",
        placeholder="Ex: 12, 15, 42",
        help="Informe um ou mais IDs de pagamento, separados por vírgula ou quebra de linha.",
    )
    submitted = st.form_submit_button("🔔 Notificar")

    if submitted:
        ids: list[int] = []
        invalid: list[str] = []
        for raw in ids_raw.replace("\n", ",").split(","):
            raw = raw.strip()
            if not raw:
                continue
            if raw.isdigit():
                ids.append(int(raw))
            else:
                invalid.append(raw)

        if invalid:
            st.warning(f"Valores inválidos ignorados: {', '.join(invalid)}")

        if not ids:
            st.warning("Informe ao menos um ID de pagamento válido.")
        else:
            try:
                with st.spinner("Enviando notificações..."):
                    result = notificar_api.notify_payments(ids)
                st.success(f"Notificação disparada para {len(ids)} cobrança(s).")
                if result:
                    st.json(result)
            except ApiError as err:
                show_api_error(err)
