import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from config import settings
from infrastructure.database.client_db import ClientDB
from application import app_registry
from .routers.api import api_router
from .errors.base import ErrorsHandler

_log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _log.info("Start server")
    asyncio.create_task(app_registry.github_stories.periodic_task(3600))
    
    await app_registry.nats_client.connect()
    await app_registry.nats_client.subscribe()
    
    yield
    _log.info("Stop server")

app = FastAPI(
    lifespan=lifespan,
    title=settings.SERVICE_NAME,
    root_path="" if settings.ROOT_PATH == "/" else settings.ROOT_PATH,
    openapi_url="/openapi.json" if settings.VIEW_DOCS else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.URLS_CORS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    async with ClientDB.session_factory() as session:
        await session.execute(text("SELECT 1"))
        return {"status": "ok"}

app.include_router(api_router)

errors_handler = ErrorsHandler(app)
