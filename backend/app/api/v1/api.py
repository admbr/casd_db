from fastapi import APIRouter, HTTPException, status
from app.api.v1.endpoints import moradores
from app.api.v1.endpoints import clientes
from app.api.v1.endpoints import pagamentos
from app.api.v1.endpoints import assinaturas
from app.api.v1.endpoints import notificar
from app.api.v1.endpoints import apartamentos
from app.api.v1.endpoints import cartoes

api_router = APIRouter()

api_router.include_router(notificar.router, prefix="/notificar", tags=["Notificar"])
api_router.include_router(moradores.router, prefix="/moradores", tags=["Moradores"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
api_router.include_router(pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])
api_router.include_router(
    assinaturas.router, prefix="/assinaturas", tags=["Assinaturas"]
)
api_router.include_router(
    apartamentos.router, prefix="/apartamentos", tags=["Apartamentos"]
)
api_router.include_router(cartoes.router, prefix="/cartoes", tags=["Cartoes"])
