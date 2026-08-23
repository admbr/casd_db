from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.src.database import init_db
from app.api.v1.api import api_router
from app import models
import httpx
from app.src.config import settings


@asynccontextmanager
async def lifspan(app: FastAPI):
    await init_db()

    global asaas_client
    asaas_client = httpx.AsyncClient(
        base_url=settings.asaas_base_url,
        headers={
            "access_token": settings.asaas_api_key,
            "Content-Type": "application/json",
        },
        timeout=15.0,
    )

    yield

    await asaas_client.aclose()


app = FastAPI(title="test", version="1.0.0")

app.include_router(router=api_router, prefix="/api/v1")
