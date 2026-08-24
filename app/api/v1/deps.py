from fastapi import Request, Depends
from app.src.asaas import AsaasClient
from app.services.billingService import BillingService
from app.services.clientService import ClientService


def get_asaas_client(request: Request) -> AsaasClient:
    return request.app.state.asaas_client


def get_billing_service(
    asaas_client: AsaasClient = Depends(get_asaas_client),
) -> BillingService:
    return BillingService(asaas_client=asaas_client)


def get_client_service(
    asaas_client: AsaasClient = Depends(get_asaas_client),
) -> ClientService:
    return ClientService(asaas_client=asaas_client)
