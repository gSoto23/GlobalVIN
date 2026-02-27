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
    
    # 5. Recent Logs (Last 15)
    stmt_logs = select(Trazabilidad).order_by(Trazabilidad.fecha_consulta.desc()).limit(15)
    result_logs = await db.execute(stmt_logs)
    recent_logs = result_logs.scalars().all()

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
    stmt_carapis = select(func.count(Trazabilidad.id)).where(Trazabilidad.proveedor == "CarApis")
    stmt_vinaudit = select(func.count(Trazabilidad.id)).where(Trazabilidad.proveedor == "VinAudit")
    
    carapis_calls = await db.scalar(stmt_carapis) or 0
    vinaudit_calls = await db.scalar(stmt_vinaudit) or 0

    return {
        "providers": {
            "CarApis": carapis_calls,
            "VinAudit": vinaudit_calls
        }
    }
