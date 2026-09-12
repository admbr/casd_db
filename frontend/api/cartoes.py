"""Calls to the /cartoes endpoints exposed by the backend."""

from typing import Any, Optional

from api.client import get, post_json


def tokenize_cartao(
    customer_id: str,
    holder_name: str,
    number: str,
    expiry_month: str,
    expiry_year: str,
    ccv: str,
    holder_email: str,
    holder_cpf_cnpj: str,
    holder_postal_code: str,
    holder_address_number: str,
    holder_phone: str,
) -> Any:
    return post_json(
        "/cartoes/",
        {
            "customer_id": customer_id,
            "card": {
                "holderName": holder_name,
                "number": number,
                "expiryMonth": expiry_month,
                "expiryYear": expiry_year,
                "ccv": ccv,
            },
            "card_holder": {
                "name": holder_name,
                "email": holder_email,
                "cpfCnpj": holder_cpf_cnpj,
                "postalCode": holder_postal_code,
                "addressNumber": holder_address_number,
                "phone": holder_phone,
            },
        },
    )


def list_cartoes(customer_id: Optional[str] = None) -> Any:
    return get("/cartoes/", {"customer_id": customer_id})
