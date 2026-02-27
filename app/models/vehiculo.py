from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from datetime import datetime, timezone
from app.db.session import Base

class VehiculoEstudio(Base):
    __tablename__ = "vehiculo_estudio"

    id = Column(Integer, primary_key=True, index=True)
    tipo_identificacion = Column(String(20), nullable=False) # VIN, CHASIS, SERIE
    identificacion = Column(String(50), unique=True, index=True, nullable=False)
    tiene_estudios = Column(Boolean, default=True)
    es_estudio_sin_registros = Column(Boolean, default=False)
    
    # Store dynamic metadata as JSON
    especificaciones_vehiculo = Column(JSON, nullable=True)
    detalle_estudio = Column(JSON, nullable=True)
    
    # PDF storage references
    url_pdf = Column(String(500), nullable=True) # Could be S3 link or local path
    pdf_hash = Column(String(100), nullable=True)
    pdf_size_bytes = Column(Integer, nullable=True)
    
    # Timestamps
    ultima_fecha_estudio = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ya_facturado_previamente = Column(Boolean, default=False)

class Trazabilidad(Base):
    __tablename__ = "trazabilidad"

    id = Column(Integer, primary_key=True, index=True)
    fecha_consulta = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    identificacion = Column(String(50), index=True)
    endpoint = Column(String(100))
    status_code = Column(Integer)
    llamada_externa = Column(Boolean, default=False) # True if we hit VinAudit/CarStat
    proveedor = Column(String(50), nullable=True) # VinAudit, CarStat, Cache
    mensaje_error = Column(String(500), nullable=True)
