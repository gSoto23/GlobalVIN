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
    
    # Provider counts for Doughnut Chart
    stmt_vincario = select(func.count(Trazabilidad.id)).where(
        and_(where_clause, Trazabilidad.proveedor == "Vincario")
    )
    stmt_vinaudit = select(func.count(Trazabilidad.id)).where(
        and_(where_clause, Trazabilidad.proveedor == "VinAudit")
    )
    count_vincario = await db.scalar(stmt_vincario) or 0
    count_vinaudit = await db.scalar(stmt_vinaudit) or 0
    
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
            "endpoint": tz.endpoint,
            "ip_origen": tz.ip_origen,
            "usuario": tz.usuario
        })

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "metrics": {
                "total": total_consultas,
                "externas": consultas_externas,
                "cache": consultas_cache,
                "errores": total_errores,
                "vincario": count_vincario,
                "vinaudit": count_vinaudit
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
            "mensaje": error.mensaje_error,
            "ip_origen": error.ip_origen,
            "usuario": error.usuario
        })
        
    return {"errors": error_list}
    
@router.get("/export")
async def export_dashboard_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Exports the main Traceability table to a CSV file.
    """
    import io
    import csv
    from fastapi.responses import StreamingResponse
    
    filters = []
    
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
            
    where_clause = and_(*filters) if filters else True

    stmt = (
        select(Trazabilidad)
        .where(where_clause)
        .order_by(Trazabilidad.fecha_consulta.desc())
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()

    # Create an in-memory string buffer
    output = io.StringIO()
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    # Write headers
    writer.writerow([
        "Fecha UTC", 
        "Criterio_Busqueda", 
        "Origen_Datos", 
        "Llamada_Externa", 
        "Codigo_Http", 
        "Usuario_B2B", 
        "IP_Origen", 
        "Endpoint", 
        "Mensaje_Error"
    ])

    for log in logs:
        fecha_str = log.fecha_consulta.strftime("%d/%m/%Y %H:%M:%S") if log.fecha_consulta else ""
        writer.writerow([
            fecha_str,
            log.identificacion or "",
            log.proveedor or "DATABASE",
            "SI" if log.llamada_externa else "NO",
            log.status_code,
            log.usuario or "N/A",
            log.ip_origen or "N/A",
            log.endpoint or "",
            log.mensaje_error or ""
        ])

    output.seek(0)
    
    filename = f"trazabilidad_racsa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/health")
async def get_system_health(db: AsyncSession = Depends(get_db)):
    """
    Checks the status of the Database and External Providers.
    Returns: green (All Good), orange (Slow/Down Providers), red (DB Error).
    """
    import httpx
    import asyncio
    
    status = "green"
    message = "Sistema En Línea"
    
    # 1. Check Database
    try:
        await db.execute(select(1))
    except Exception as e:
        return {"color": "red", "message": "Sistema Caído (BD)"}
        
    # 2. Check Providers (Concurrent Pings)
    vinaudit_url = "https://api.vinaudit.com"
    vincario_url = "https://api.vincario.com"
    
    async def ping(url):
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                # We just care that it responded, even a 403 or 401 is "up"
                return True
        except:
            return False

    results = await asyncio.gather(ping(vinaudit_url), ping(vincario_url))
    
    if not all(results):
        status = "orange"
        message = "Proveedores Lentos"
        
    return {"color": status, "message": message}
