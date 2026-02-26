from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class TrazabilidadResponse(BaseModel):
    id: int
    fecha_consulta: datetime
    identificacion: str
    endpoint: str
    status_code: int
    llamada_externa: bool
    proveedor: Optional[str] = None
    mensaje_error: Optional[str] = None

    class Config:
        from_attributes = True

class TrazabilidadPagination(BaseModel):
    total: int
    items: List[TrazabilidadResponse]
