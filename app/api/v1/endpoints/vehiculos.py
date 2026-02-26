from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any
import datetime

from app.db.session import get_db
from app.models.vehiculo import VehiculoEstudio, Trazabilidad
from app.schemas.vehiculo import EstudioBaseResponse, EstudioCompletoResponse, PdfInfo
from app.core.security import verify_token
from app.services.provider_client import orchestrate_vin_search
from app.services.normalizer import normalize_provider_data

router = APIRouter()

@router.get("/existencia", response_model=EstudioBaseResponse)
async def check_estudio_existencia(
    tipoIdentificacion: str = Query(..., description="VIN, CHASIS, SERIE"),
    identificacion: str = Query(..., description="El valor del VIN/chasis/número de serie"),
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_token)
) -> Any:
    """
    Verify if a vehicle study exists internally without making external calls.
    """
    if tipoIdentificacion not in ["VIN", "CHASIS", "SERIE"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tipoIdentificacion must be VIN, CHASIS, or SERIE"
        )
        
    stmt = select(VehiculoEstudio).where(VehiculoEstudio.identificacion == identificacion)
    result = await db.execute(stmt)
    estudio = result.scalar_one_or_none()
    
    # Log the Traceability
    trazabilidad = Trazabilidad(
        identificacion=identificacion,
        endpoint="/api/v1/vehiculos/estudios/existencia",
        status_code=200,
        llamada_externa=False,
        proveedor="Cache" if estudio else None
    )
    db.add(trazabilidad)
    await db.commit()
    
    if not estudio:
        # User requested 200 OK even if false for this specific endpoint
        return EstudioBaseResponse(
            tipoIdentificacion=tipoIdentificacion,
            identificacion=identificacion,
            tieneEstudios=False,
            ultimaFechaEstudio=None
        )
        
    return EstudioBaseResponse(
        tipoIdentificacion=estudio.tipo_identificacion,
        identificacion=estudio.identificacion,
        tieneEstudios=estudio.tiene_estudios,
        ultimaFechaEstudio=estudio.ultima_fecha_estudio
    )

@router.get("", response_model=EstudioCompletoResponse)
async def get_estudio_completo(
    tipoIdentificacion: str = Query(..., description="VIN, CHASIS, SERIE"),
    identificacion: str = Query(..., description="El valor del VIN/chasis/número de serie"),
    db: AsyncSession = Depends(get_db),
    token_data: dict = Depends(verify_token)
) -> Any:
    """
    Get full vehicle study. Fetches from DB cache or reaches out to external provider.
    """
    if tipoIdentificacion not in ["VIN", "CHASIS", "SERIE"]:
        raise HTTPException(status_code=400, detail="tipoIdentificacion must be VIN, CHASIS, or SERIE")

    # 1. Check Internal Database
    stmt = select(VehiculoEstudio).where(VehiculoEstudio.identificacion == identificacion)
    result = await db.execute(stmt)
    estudio_db = result.scalar_one_or_none()

    if_llamada_externa = False
    proveedor_usado = "Cache"

    if not estudio_db:
        # 2. Not found locally, call External Provider
        if_llamada_externa = True
        try:
            raw_data, proveedor_usado, raw_pdf_content = await orchestrate_vin_search(identificacion)
            
            # Normalize Response
            meta, detalle, es_sin_registros = normalize_provider_data(proveedor_usado, raw_data)
            
            # Create Database Record
            now_utc = datetime.datetime.now(datetime.timezone.utc)
            estudio_db = VehiculoEstudio(
                tipo_identificacion=tipoIdentificacion,
                identificacion=identificacion,
                tiene_estudios=True,
                es_estudio_sin_registros=es_sin_registros,
                metadatos_vehiculo=meta.model_dump(),
                detalle_estudio=detalle.model_dump(),
                url_pdf="local://blob_storage/" + identificacion + ".pdf",
                pdf_hash="sha256:dummyhash123", # Usually hashlib.sha256(raw_pdf_content.encode()).hexdigest()
                pdf_size_bytes=len(raw_pdf_content),
                ultima_fecha_estudio=now_utc,
                ya_facturado_previamente=True
            )
            db.add(estudio_db)
            # Commit to ensure it's saved for future requests
            await db.commit()
            await db.refresh(estudio_db)

        except Exception as e:
            # Failed to fetch from external provider
            trazabilidad = Trazabilidad(
                identificacion=identificacion, endpoint="/api/v1/vehiculos/estudios",
                status_code=502, llamada_externa=True, proveedor=proveedor_usado, mensaje_error=str(e)
            )
            db.add(trazabilidad)
            await db.commit()
            raise HTTPException(status_code=502, detail="External Provider Error")

    # Prepare PDF Output
    # In reality you would load the Base64 from S3 here
    mock_base64_pdf = "JVBERi0xLjQKJ_MOCK_PDF_CONTENT..." if if_llamada_externa else "JVBERi0xLjQKJ_LOADED_FROM_CACHE..."
    
    pdf_info = PdfInfo(
        content=mock_base64_pdf,
        tamañoBytes=estudio_db.pdf_size_bytes,
        hash=estudio_db.pdf_hash,
        fechaGeneracion=estudio_db.ultima_fecha_estudio,
        yaFacturadoPreviamente=estudio_db.ya_facturado_previamente
    )

    # Log Traceability
    trazabilidad = Trazabilidad(
        identificacion=identificacion,
        endpoint="/api/v1/vehiculos/estudios",
        status_code=200,
        llamada_externa=if_llamada_externa,
        proveedor=proveedor_usado
    )
    db.add(trazabilidad)
    await db.commit()

    return EstudioCompletoResponse(
        tipoIdentificacion=estudio_db.tipo_identificacion,
        identificacion=estudio_db.identificacion,
        tieneEstudios=estudio_db.tiene_estudios,
        ultimaFechaEstudio=estudio_db.ultima_fecha_estudio,
        esEstudioSinRegistros=estudio_db.es_estudio_sin_registros,
        metadatosVehiculo=estudio_db.metadatos_vehiculo,
        detalleEstudio=estudio_db.detalle_estudio,
        pdf=pdf_info
    )
