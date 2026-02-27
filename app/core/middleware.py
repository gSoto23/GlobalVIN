import uuid
import logging
from loguru import logger
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
import time

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        start_time = time.time()
        
        # Log request start
        logger.info(f"[{correlation_id}] {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log request end
        logger.info(f"[{correlation_id}] Completed {response.status_code} in {process_time:.3f}s")
        
        return response

def setup_exception_handlers(app: FastAPI):
    
    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        
        # Determine code from detail if it's a dict, otherwise generate a generic one
        if isinstance(exc.detail, dict) and "codigo" in exc.detail:
            error_response = exc.detail
        else:
            codigo = "ERROR_BAD_REQUEST" if exc.status_code == 400 else "ERROR_UNAUTHORIZED" if exc.status_code == 401 else "ERROR_FORBIDDEN" if exc.status_code == 403 else "ERROR_NOT_FOUND" if exc.status_code == 404 else "ERROR_INTERNAL"
            error_response = {
                "codigo": codigo,
                "mensaje": "Se ha producido un error",
                "detalle": str(exc.detail),
                "correlationId": correlation_id
            }
            
        # Ensure CorrelationID is present
        error_response["correlationId"] = correlation_id

        logger.error(f"[{correlation_id}] HTTP {exc.status_code}: {error_response}")
        return JSONResponse(status_code=exc.status_code, content=error_response)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        
        error_response = {
            "codigo": "ERROR_VALIDACION_DATOS",
            "mensaje": "Los datos proporcionados no son válidos.",
            "detalle": exc.errors(),
            "correlationId": correlation_id
        }
        
        logger.error(f"[{correlation_id}] Validation Error: {error_response}")
        return JSONResponse(status_code=400, content=error_response)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        correlation_id = getattr(request.state, "correlation_id", "unknown")
        
        error_response = {
            "codigo": "ERROR_INTERNO_SERVIDOR",
            "mensaje": "Ocurrió un error inesperado al procesar la solicitud.",
            "detalle": str(exc),
            "correlationId": correlation_id
        }
        
        logger.exception(f"[{correlation_id}] Unhandled Exception: {exc}")
        return JSONResponse(status_code=500, content=error_response)
