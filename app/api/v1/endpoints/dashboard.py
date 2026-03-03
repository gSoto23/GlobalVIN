from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from fastapi.templating import Jinja2Templates
import os

from app.db.session import get_db
from app.models.vehiculo import Trazabilidad, VehiculoEstudio

router = APIRouter()

# Get absolute path for templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("", response_class=HTMLResponse)
async def get_dashboard_ui(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Renders the operational dashboard UI with optional date filtering.
    """
    
    # Base filter list (empty by default)
    filters = []
    
    # Process dates if provided
    if start_date:
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d")
            filters.append(Trazabilidad.fecha_consulta >= sd)
        except ValueError:
            pass
            
    if end_date:
        try:
            # End of day
            ed = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            filters.append(Trazabilidad.fecha_consulta <= ed)
        except ValueError:
            pass
            
    # Combine filters into a single AND condition if they exist
    where_clause = and_(*filters) if filters else True

    # 1. Total Queries
    stmt_total = select(func.count(Trazabilidad.id)).where(where_clause)
    total_consultas = await db.scalar(stmt_total) or 0
    
    # 2. Queries with External Calls (Billed by provider)
    stmt_external = select(func.count(Trazabilidad.id)).where(
        and_(where_clause, Trazabilidad.llamada_externa == True)
    )
    consultas_externas = await db.scalar(stmt_external) or 0
    
    # 3. Queries from Cache (Reused/Free)
    consultas_cache = total_consultas - consultas_externas
    
    # 4. Total Errors (Non-200)
    stmt_errors = select(func.count(Trazabilidad.id)).where(
        and_(where_clause, Trazabilidad.status_code != 200)
    )
    total_errores = await db.scalar(stmt_errors) or 0
    
    # 5. Recent Logs (All logs with joined VehiculoEstudio for PDF url)
    stmt_logs = (
        select(Trazabilidad, VehiculoEstudio.url_pdf)
        .outerjoin(VehiculoEstudio, Trazabilidad.identificacion == VehiculoEstudio.identificacion)
        .where(where_clause)
        .order_by(Trazabilidad.fecha_consulta.desc())
    )
    result_logs = await db.execute(stmt_logs)
    
    # Pack into a list of dicts for Jinja
    recent_logs = []
    for tz, pdf_url in result_logs:
        recent_logs.append({
            "fecha_consulta": tz.fecha_consulta,
            "identificacion": tz.identificacion,
            "proveedor": tz.proveedor,
            "llamada_externa": tz.llamada_externa,
            "status_code": tz.status_code,
            "mensaje_error": tz.mensaje_error,
            "url_pdf": pdf_url,
            "endpoint": tz.endpoint
        })

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "metrics": {
                "total": total_consultas,
                "externas": consultas_externas,
                "cache": consultas_cache,
                "errores": total_errores
            },
            "logs": recent_logs,
            "current_start": start_date or "",
            "current_end": end_date or ""
        }
    )

@router.get("/metrics")
async def get_metrics_json(db: AsyncSession = Depends(get_db)):
    """
    Returns metrics as JSON for potential charting or external tracking.
    """
    # Simply reusing basic counts for now
    stmt_vincario = select(func.count(Trazabilidad.id)).where(Trazabilidad.proveedor == "Vincario")
    stmt_vinaudit = select(func.count(Trazabilidad.id)).where(Trazabilidad.proveedor == "VinAudit")
    
    vincario_calls = await db.scalar(stmt_vincario) or 0
    vinaudit_calls = await db.scalar(stmt_vinaudit) or 0

    return {
        "providers": {
            "Vincario": vincario_calls,
            "VinAudit": vinaudit_calls
        }
    }

@router.get("/errors")
async def get_dashboard_errors(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a JSON list of detailed error logs (status != 200)
    used to feed the SLAs dashboard modal dynamically.
    """
    filters = [Trazabilidad.status_code != 200]
    
    if start_date:
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d")
            filters.append(Trazabilidad.fecha_consulta >= sd)
        except ValueError:
            pass
            
    if end_date:
        try:
            ed = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            filters.append(Trazabilidad.fecha_consulta <= ed)
        except ValueError:
            pass
            
    stmt = (
        select(Trazabilidad)
        .where(and_(*filters))
        .order_by(Trazabilidad.fecha_consulta.desc())
    )
    result = await db.execute(stmt)
    errors = result.scalars().all()
    
    error_list = []
    for error in errors:
        error_list.append({
            "fecha": error.fecha_consulta.strftime("%d/%m/%Y %H:%M:%S") if error.fecha_consulta else "N/A",
            "vin": error.identificacion,
            "proveedor": error.proveedor or "Local",
            "endpoint": error.endpoint,
            "status_code": error.status_code,
            "mensaje": error.mensaje_error
        })
        
    return {"errors": error_list}
