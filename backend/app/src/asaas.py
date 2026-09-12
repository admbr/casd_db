from typing import Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx
from fastapi import HTTPException, status
from app.models.cliente import ClienteCreate
from app.models.pagamento import PagamentoCreate
import json
import logging

logger = logging.getLogger(__name__)


class AsaasClient:
    def __init__(self, asaas_client: httpx.AsyncClient):
        self.client = asaas_client

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        try:
            if method.upper() == "GET":
                response = await self.client.request(method, endpoint, params=data)
            else:
                response = await self.client.request(method, endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
            except (json.JSONDecodeError, ValueError):
                error_detail = e.response.text

            logger.error(
                "Asaas API error %s on %s %s: %r",
                e.response.status_code,
                method,
                endpoint,
                error_detail,
            )

            raise HTTPException(
                status_code=e.response.status_code,
                detail={"message": "Asaas API Error", "error": error_detail},
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to communicate with Asaas gateway: {str(e)}",
            )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=16), reraise=True
    )
    async def get_or_create_customer(
        self,
        nome: str,
        cpf_cnpj: str,
    ) -> dict[str, Any]:
        batch_size = 1
        offset = 0
        while batch_size >= 1:
            response = await self._request(
                "GET",
                "/customers",
                data={
                    "offset": offset,
                    "limit": 100,
                    "cpfCnpj": cpf_cnpj,
                },
            )
            offset += 100
            batch_size = len(response["data"])
            for client in response["data"]:
                if client["cpfCnpj"] == cpf_cnpj:
                    client["criado"] = False
                    return client
        payload = {
            "name": nome,
            "cpfCnpj": cpf_cnpj,
            "notificationDisabled": True,
        }
        client = await self._request("POST", "/customers", data=payload)
        client["criado"] = True
        return client

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=16), reraise=True
    )
    async def list_all_customers(self) -> list[ClienteCreate]:
        offset = 0
        clients = []
        while True:
            response = await self._request(
                "GET",
                "/customers",
                data={
                    "offset": offset,
                    "limit": 100,
                },
            )
            offset += 100
            data = response.get("data")
            if data:
                for customer in data:
                    clients.append(
                        ClienteCreate(
                            deleted=customer["deleted"],
                            email=customer["email"],
                            name=customer["name"],
                            cpf_cnpj=customer["cpfCnpj"],
                            date_created=customer["dateCreated"],
                            notification_disabled=customer["notificationDisabled"],
                            cliente_id=customer["id"],
                            morador_id=None,
                        )
                    )
            else:
                return clients

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=16), reraise=True
    )
    async def list_all_payments(self) -> list[PagamentoCreate]:
        offset = 0
        payments = []
        while True:
            response = await self._request(
                "GET",
                "/payments",
                data={
                    "offset": offset,
                    "limit": 100,
                },
            )
            offset += 100
            data = response.get("data")
            if data:
                for payment in data:
                    payments.append(
                        PagamentoCreate(
                            asaas_id=payment["id"],
                            customer_id=payment["customer"],
                            deleted=payment["deleted"],
                            value=payment["value"],
                            client_payment_date=payment["clientPaymentDate"],
                            date_created=payment["dateCreated"],
                            due_date=payment["dueDate"],
                            invoice_number=payment["invoiceNumber"],
                            invoice_url=payment["invoiceUrl"],
                            net_value=payment["netValue"],
                            original_due_date=payment["originalDueDate"],
                            payment_date=payment["paymentDate"],
                            description=payment["description"],
                            status=payment["status"],
                            billing_type=payment["billingType"],
                            bank_slip_url=payment["bankSlipUrl"],
                        )
                    )
            else:
                return payments

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=16), reraise=True
    )
    async def del_payment_by_id(self, id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/payments/{id}")

    async def del_client_by_id(self, id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/customers/{id}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=16), reraise=True
    )
    async def create_payment(
        self,
        payment_in: PagamentoCreate,
    ) -> PagamentoCreate:
        payload = {
            "customer": payment_in.customer_id,
            "billingType": payment_in.billing_type,
            "value": payment_in.value,
            "dueDate": payment_in.due_date.isoformat(),
            "description": payment_in.description,
            "postalService": False,
        }
        payment = await self._request(
            "POST",
            "/payments",
            data=payload,
        )
        return PagamentoCreate(
            asaas_id=payment["id"],
            customer_id=payment["customer"],
            deleted=payment["deleted"],
            value=payment["value"],
            client_payment_date=payment["clientPaymentDate"],
            date_created=payment["dateCreated"],
            due_date=payment["dueDate"],
            invoice_number=payment["invoiceNumber"],
            invoice_url=payment["invoiceUrl"],
            net_value=payment["netValue"],
            original_due_date=payment["originalDueDate"],
            payment_date=payment["paymentDate"],
            description=payment["description"],
            status=payment["status"],
            billing_type=payment["billingType"],
        )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=16), reraise=True
    )
    async def tokenize_credit_card(
        self,
        customer_id: str,
        credit_card: dict,
        holder_info: dict,
        remote_ip: str,
    ) -> dict[str, Any]:
        payload = {
            "customer": customer_id,
            "creditCard": credit_card,
            "creditCardHolderInfo": holder_info,
            "remoteIp": remote_ip,
        }
        return await self._request("POST", "/creditCard/tokenize", data=payload)

    async def create_subscription(
        self,
        customer_id: str,
        value: float,
        next_due_date: str,
        description: str,
        credit_card_token: str,
        remote_ip: str,
        cycle: str = "MONTHLY",
    ) -> dict[str, Any]:
        payload = {
            "customer": customer_id,
            "billingType": "CREDIT_CARD",
            "value": value,
            "nextDueDate": next_due_date,
            "cycle": cycle,
            "description": description,
            "creditCardToken": credit_card_token,
            "remoteIp": remote_ip,
        }
        return await self._request("POST", "/subscription", data=payload)

    async def cancel_subscription(self, subscription_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"subscriptions/{subscription_id}")

    async def get_subscription(self, subscription_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/subscriptions/{subscription_id}")

    async def list_subscription_payments(self, subscription_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/subscriptions/{subscription_id}/payments")
