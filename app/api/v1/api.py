from fastapi import APIRouter
from app.api.v1.endpoints import vehiculos, trazabilidad, dashboard, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(vehiculos.router, prefix="/vehiculos/estudios", tags=["Consultas de Estudio VIN"])
api_router.include_router(trazabilidad.router, prefix="/trazabilidad", tags=["Trazabilidad"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
