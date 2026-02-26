# GlobalVIN API 🚗

API RESTful diseñada en **FastAPI** para consultar historiales de vehículos importados desde Estados Unidos y Corea del Sur.

## Características Principales
*   **Enrutamiento Dinámico por WMI:** Identifica el país de origen a partir del VIN e invoca a proveedores externos Mock (VinAudit / CarStat).
*   **Asíncrono:** Arquitectura de alto desempeño (`async/await`) con SQLAlchemy 2.0.
*   **Trazabilidad Inteligente:** Almacena resultados en base de datos para no cobrar dos veces por el mismo VIN, y mantiene logs operativos.
*   **Swagger Integrado:** Autogeneración de documentación OpenAPI en la ruta `/docs`.

## Instalación y Configuración

```bash
# 1. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Arrancar servidor de desarrollo
uvicorn main:app --reload --port 8080
```

## Endpoints Disponibles

1. **`GET /api/v1/vehiculos/estudios/existencia`**: Valida si el estudio de un VIN ya existe en caché (BD interna).
2. **`GET /api/v1/vehiculos/estudios`**: Endpoint principal. Obtiene el estudio (Caché local o API Externa) y retorna metadatos del auto y PDF (Mock).
3. **`GET /api/v1/trazabilidad`**: Visualización de los logs de Trazabilidad para Dashboard operativo.

## Seguridad (JWT)
Todas las llamadas al API `/api/v1/vehiculos` y `/api/v1/trazabilidad` requieren el envío de cabecera:
`Authorization: Bearer <TOKEN>`
El token debe poseer el scope `vehiculos.estudios.read`.
