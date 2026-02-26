from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Any

from app.db.session import get_db
from app.models.vehiculo import Trazabilidad
from app.schemas.trazabilidad import TrazabilidadPagination
from app.core.security import verify_token

router = APIRouter()

@router.get("", response_model=TrazabilidadPagination)
async def get_trazabilidad_logs(
    skip: int = Query(0, ge=0, description="Registros a omitir (paginación)"),
    limit: int = Query(50, ge=1, le=100, description="Cantidad de registros a devolver"),
    identificacion: str = Query(None, description="Filtrar por VIN/Chasis específico"),
    db: AsyncSession = Depends(get_db),
    # Requiring token validation for admin endpoints (we could use another scope like vehiculos.admin)
    token_data: dict = Depends(verify_token) 
) -> Any:
    """
    Obtener registro de trazabilidad y logs de llamadas a proveedores (Dashboard Operativo).
    """
    stmt = select(Trazabilidad)
    count_stmt = select(func.count(Trazabilidad.id))
    
    if identificacion:
        stmt = stmt.where(Trazabilidad.identificacion == identificacion)
        count_stmt = count_stmt.where(Trazabilidad.identificacion == identificacion)
        
    stmt = stmt.order_by(desc(Trazabilidad.fecha_consulta)).offset(skip).limit(limit)
    
    # Execute Queries
    total_result = await db.execute(count_stmt)
    total_count = total_result.scalar()
    
    items_result = await db.execute(stmt)
    items = items_result.scalars().all()
    
    return TrazabilidadPagination(
        total=total_count,
        items=items
    )
