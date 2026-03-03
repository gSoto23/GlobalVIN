from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi.templating import Jinja2Templates
import os

from app.db.session import get_db
from app.models.vehiculo import Trazabilidad, VehiculoEstudio

router = APIRouter()

# Get absolute path for templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# BASE_DIR evalúa a .../globalvin-api/app
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("", response_class=HTMLResponse)
async def get_dashboard_ui(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Renders the operational dashboard UI.
    """
    # 1. Total Queries
    stmt_total = select(func.count(Trazabilidad.id))
    total_consultas = await db.scalar(stmt_total) or 0
    
    # 2. Queries with External Calls (Billed by provider)
    stmt_external = select(func.count(Trazabilidad.id)).where(Trazabilidad.llamada_externa == True)
    consultas_externas = await db.scalar(stmt_external) or 0
    
    # 3. Queries from Cache (Reused/Free)
    consultas_cache = total_consultas - consultas_externas
    
    # 4. Total Errors (Non-200)
    stmt_errors = select(func.count(Trazabilidad.id)).where(Trazabilidad.status_code != 200)
    total_errores = await db.scalar(stmt_errors) or 0
    
    # 5. Recent Logs (All logs with joined VehiculoEstudio for PDF url)
    stmt_logs = (
        select(Trazabilidad, VehiculoEstudio.url_pdf)
        .outerjoin(VehiculoEstudio, Trazabilidad.identificacion == VehiculoEstudio.identificacion)
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
            "url_pdf": pdf_url
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
            "logs": recent_logs
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
