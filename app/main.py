from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.src.database import init_db
from app.api.v1.api import api_router
from app import models
import httpx
from app.src.config import settings
from app.src.asaas import AsaasClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    global asaas_client_conn
    global aeita_asaas_client_conn
    asaas_client_conn = httpx.AsyncClient(
        base_url=settings.asaas_base_url,
        headers={
            "access_token": settings.asaas_api_key,
            "Content-Type": "application/json",
        },
        timeout=15.0,
    )
    aeita_asaas_client_conn = httpx.AsyncClient(
        base_url=settings.asaas_base_url,
        headers={
            "access_token": settings.aeita_asaas_api_key,
            "Content-Type": "application/json",
        },
        timeout=15.0,
    )

    app.state.asaas_client = AsaasClient(asaas_client_conn)
    app.state.aeita_asaas_client = AsaasClient(aeita_asaas_client_conn)

    yield

    await asaas_client_conn.aclose()
    await aeita_asaas_client_conn.aclose()


app = FastAPI(title="test", version="1.0.0", lifespan=lifespan)

app.include_router(router=api_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
