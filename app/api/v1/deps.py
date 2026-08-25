from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.src.asaas import AsaasClient
from app.services.billingService import BillingService
from app.services.clientService import ClientService
from app.src.database import get_session


def get_asaas_client(request: Request) -> AsaasClient:
    return request.app.state.asaas_client


def get_billing_service(
    asaas_client: AsaasClient = Depends(get_asaas_client),
    db_session: AsyncSession = Depends(get_session),
) -> BillingService:
    return BillingService(asaas_client=asaas_client, db_session=db_session)


def get_client_service(
    asaas_client: AsaasClient = Depends(get_asaas_client),
    db_session: AsyncSession = Depends(get_session),
) -> ClientService:
    return ClientService(asaas_client=asaas_client, db_session=db_session)
