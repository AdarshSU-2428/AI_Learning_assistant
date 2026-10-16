from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.dependencies import app_service
from backend.routes import router
from config.settings import DOCUMENTS_PATH


@asynccontextmanager
async def lifespan(app):
    yield


app = FastAPI(
    title="AI Learning Assistant",
    description="AI Learning Assistant Backend API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
