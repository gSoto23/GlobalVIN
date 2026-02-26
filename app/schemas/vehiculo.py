from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class EstudioBaseResponse(BaseModel):
    tipoIdentificacion: str = Field(..., description="VIN, CHASIS, SERIE")
    identificacion: str
    tieneEstudios: bool
    ultimaFechaEstudio: Optional[datetime] = None

class Dimensiones(BaseModel):
    alturaCm: Optional[float] = None
    longitudCm: Optional[float] = None
    anchoCm: Optional[float] = None

class MetadatosVehiculo(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    anio: Optional[int] = None
    version: Optional[str] = None
    paisOrigen: Optional[str] = None
    tipoCombustible: Optional[str] = None
    motor: Optional[str] = None
    colorExterior: Optional[str] = None
    tipoTransmision: Optional[str] = None
    tipoCarroceria: Optional[str] = None
    dimensiones: Optional[Dimensiones] = None
    # Flexible catch-all for extra data
    model_config = ConfigDict(extra="allow")

class DetalleEstudio(BaseModel):
    tieneAccidentesRegistrados: bool = False
    tienePerdidaTotal: bool = False
    tieneRegistrosSubasta: bool = False
    tieneProblemasVerificados: bool = False
    tieneGravamenes: bool = False
    tieneRegistrosRobo: bool = False
    # Catch-all for sub-lists like 'titulos', 'accidentes'
    model_config = ConfigDict(extra="allow")

class PdfInfo(BaseModel):
    content: Optional[str] = None # Base64
    tamañoBytes: Optional[int] = None
    hash: Optional[str] = None
    fechaGeneracion: Optional[datetime] = None
    yaFacturadoPreviamente: bool = False

class EstudioCompletoResponse(EstudioBaseResponse):
    esEstudioSinRegistros: bool = False
    metadatosVehiculo: Optional[MetadatosVehiculo] = None
    detalleEstudio: Optional[DetalleEstudio] = None
    pdf: Optional[PdfInfo] = None
