import os
import hashlib
from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, Tuple
from app.schemas.vehiculo import EspecificacionesVehiculo, DetalleEstudio

# Optional: Import pdfkit if installed, otherwise we'll create a mock for local dev
try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(BASE_DIR, "app/templates")

# Ensure storage directory exists
STORAGE_DIR = os.path.join(BASE_DIR, "storage", "pdfs")
os.makedirs(STORAGE_DIR, exist_ok=True)

# Jinja2 setup
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

async def generate_racsa_pdf(
    vin: str, 
    meta: 'EspecificacionesVehiculo', 
    detalle: 'DetalleEstudio', 
    es_sin_registros: bool
) -> Tuple[str, str, int]:
    """
    Generates a PDF report meeting RACSA's requirements.
    Returns: (pdf_path, pdf_hash, size_in_bytes)
    """
    
    # 1. Render HTML Template
    template = env.get_template("reporte_base.html")
    
    html_out = template.render(
        vin=vin,
        meta=meta,
        detalle=detalle,
        es_sin_registros=es_sin_registros,
        fecha_generacion=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    
    filename = f"{vin}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(STORAGE_DIR, filename)
    
    # 2. Convert HTML to PDF
    if PDFKIT_AVAILABLE:
        try:
            # Requires wkhtmltopdf installed on the system
            pdfkit.from_string(html_out, filepath, options={"enable-local-file-access": ""})
            
            with open(filepath, "rb") as f:
                pdf_bytes = f.read()
                
        except Exception as e:
            # Fallback for local development if wkhtmltopdf is missing
            print(f"Warning: PDF generation failed ({e}). Mocking PDF.")
            pdf_bytes = b"%PDF-1.4\n%MOCK_DEVELOPMENT_PDF\n"
            with open(filepath, "wb") as f:
                f.write(pdf_bytes)
    else:
        # Save mock text if library is not installed
        pdf_bytes = b"%PDF-1.4\n%MOCK_DEVELOPMENT_PDF\n"
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
            
    # Calculate Hash and Size
    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
    size_bytes = len(pdf_bytes)
    
    # Normally we would upload to S3 here and return the S3 URL.
    # For now, we return the local URL/Path.
    return filepath, f"sha256:{pdf_hash}", size_bytes
