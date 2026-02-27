from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, Base
from app.core.middleware import CorrelationIDMiddleware, setup_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables in SQLite/Postgres (development only)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API para obtención de historial de vehículos VIN (EE. UU. y Corea del Sur)",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Setup custom exception handlers for RACSA format
setup_exception_handlers(app)

# Add CorrelationID middleware
app.add_middleware(CorrelationIDMiddleware)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def root():
    return {"status": "ok", "message": "GlobalVIN API is running"}
