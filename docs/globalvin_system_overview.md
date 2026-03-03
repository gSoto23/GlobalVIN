# GlobalVIN - Motor de Trazabilidad Vehicular

## 1. Objetivo del Sistema
GlobalVIN es una API intermediaria (Middleware) diseñada para consultar, normalizar y estandarizar reportes de historial de vehículos emitidos en el extranjero (Estados Unidos, Canadá, Corea del Sur), cumpliendo estrictamente con los requerimientos legales y técnicos de inspección vehicular estipulados en la contratación (ej: RACSA).

## 2. Flujo de Operación General
El sistema funciona bajo el siguiente ciclo de vida por cada consulta de VIN:

1.  **Recepción de Consulta (API Request):**
    *   Cliente envía un VIN al endpoint `/api/v1/estudios/vin/{vin}`.
2.  **Detección de Origen (WMI Detector):**
    *   La API analiza los primeros 3 caracteres del VIN (WMI - *World Manufacturer Identifier*).
    *   Determina automáticamente si el VIN pertenece a Norteamérica, Corea del Sur, Japón, Europa, etc.
3.  **Enrutamiento Inteligente al Proveedor (Provider Client):**
    *   **VinAudit:** Se utiliza para despachar vehículos de Estados Unidos y Canadá.
    *   **Vincario:** Se utiliza para despachar vehículos de Corea del Sur e Internacionales.
4.  **Normalización de Datos:**
    *   La respuesta cruda (RAW JSON) del proveedor se procesa a través del archivo modular `normalizer.py`.
    *   Independientemente de quién sea el proveedor, el sistema mapea los accidentes, robos, títulos, ventas, especificaciones y marcas de salvamento a un **ÚNICO esquema estandarizado (Pydantic)** requerido por el cartel de contratación.
5.  **Generación de Reporte PDF (RACSA Compliance):**
    *   La data estandarizada se inyecta en una plantilla HTML (`reporte_base.html`) diseñada con los colores corporativos y estética del nuevo Dashboard.
    *   El motor genera un documento PDF legible y calcula un HASH SHA-256 de seguridad para garantizar autenticidad ante instancias auditoras.
6.  **Respuesta Final (Response):**
    *   La API de GlobalVIN responde al cliente con un JSON limpio, unificado y fácil de leer, incluyendo el estado de alertas, los datos suplementarios documentados y el HASH de validación del PDF generado.

## 3. Estado Actual de la Integración

### VinAudit (Estados Unidos y Canadá) - ✅ Completado y Validado (PRODUCCIÓN)
*   **Conexión:** API conectada con llaves de producción reales de VinAudit.
*   **Mapeo:** El modelo extrae exitosamente: Especificaciones Básicas, Historial de Títulos/Odómetro, Transacciones de Ventas y Alertas Críticas (Salvage/Junk/Accidents).
*   **Pruebas:** Se realizaron transacciones exitosas que validan el mapeo tanto de un vehículo "Limpio" (Clean) como un vehículo "Pérdida Total" (Junk/Salvage con colisión trasera verificado).
*   **PDF:** Plantilla renderizada exitosamente con inyección dinámica de datos contractuales e información de Valor Agregado suplementaria.

### Vincario (Corea del Sur) - ⏳ Desarrollado, Pendiente de Validar con Datos Reales
*   **Conexión:** Orquestador de solicitudes y variables integradas listos en código.
*   **Mapeo:** Normalizador desarrollado en base a la documentación técnica oficial de Vincario (estructuras divididas, market data vs equipment/tech data).
*   **Pruebas:** **ESTADO: EN ESPERA.** Al no contar con credenciales aprobadas o créditos de producción en la plataforma de Vincario, no se ha podido enviar un VIN coreano real a la red. Estamos pendientes de que se apruebe la cuenta para hacer la primera petición real y garantizar que la respuesta json aterrice correctamente sobre nuestro `normalizer.py`.

## 4. Arquitectura y Estructura del Proyecto en Código
La arquitectura del proyecto sigue un estándar limpio enfocado en Microservicios / API REST con FastAPI en Python:

*   `/app/api/endpoints/` : Define los "Controladores" de las rutas REST (ej: dónde llega la petición de `/vin`).
*   `/app/services/provider_client.py` : Orquestador maestro que conecta con servidores externos (VinAudit / Vincario) vía solicitudes HTTP.
*   `/app/services/wmi_detector.py` : Analizador léxico y diccionario de orígenes geográficos del carro basado en su chasis.
*   `/app/services/normalizer.py` : El "cerebro traductor" encargado de leer un JSON complejo y de estructura variable, y convertirlo al formato simple y siempre igual exigido por contrato.
*   `/app/services/pdf_generator.py` : Motor basado en Jinja2 que genera los PDFs locales o virtuales para certificar la consulta.
*   `/app/templates/reporte_base.html` : Interfaz gráfica/visual de lo que el cliente final leerá en el PDF exportado.
*   `/app/schemas/` : Modelos Pydantic utilizados como "Contratos de Datos" que validan estrictamente qué variables y tipos de datos pueden entrar y salir de la API.
*   `/docs/` : Almacena referencias técnicas estáticas (ej: respuestas json puras y arquitectura) para futuras pruebas u orientaciones técnicas de nuevo personal.
