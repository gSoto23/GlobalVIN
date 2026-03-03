# GlobalVIN - Documentación Técnica y Operativa

## 1. Resumen Ejecutivo
**GlobalVIN** es un ecosistema de backend transaccional (API RESTful) y panel de control operativo desarrollado para RACSA. Su objetivo primordial es unificar, consultar y almacenar el historial técnico, legal y de accidentes de vehículos importados desde múltiples regiones geográficas (Estados Unidos, Canadá, Corea del Sur y el resto de Europa/Asia) a través de un único punto de integración.

El sistema actúa como un **Middleware Inteligente** que toma decisiones de enrutamiento basadas en el Identificador del Vehículo (VIN), interactúa con proveedores de datos globales, estructura la información de manera homogénea, genera reportes PDF formales, y protege los SLAs de la institución mediante facturación controlada, caché de ahorro y trazabilidad inmutable.

---

## 2. Arquitectura del Ecosistema

El sistema está construido sobre una arquitectura moderna, asíncrona y orientada a microservicios utilizando Python.

- **Framework Principal:** [FastAPI](https://fastapi.tiangolo.com/) (Escogido por su altísimo rendimiento asíncrono y auto-generación de documentación OpenAPI/Swagger).
- **Motor de Base de Datos:** `SQLite` con drivers asíncronos (`aiosqlite`), mapeado a través del ORM **SQLAlchemy 2.0**. La arquitectura agnóstica de SQLAlchemy permite que el sistema pueda migrarse a **PostgreSQL** o **SQL Server** en producción cambiando únicamente la cadena de conexión.
- **Renderizado de Interfaz (Dashboard):** Motor de plantillas **Jinja2** integrado en FastAPI, estilizado con **Tailwind CSS** vía CDN para no engrosar el peso del repositorio, y componentes dinámicos administrados con Vanilla JS, jQuery y **SweetAlert2**.
- **Generación de Reportes:** `pdfkit` respaldado por `wkhtmltopdf` para conversiones perfectas de HTML a PDF.

---

## 3. Flujo Lógico y Cumplimiento de Contratación

El sistema cumple rigurosamente con los requisitos contractuales y de negocio a través del siguiente flujo de operación cuando un cliente B2B o interfaz consulta un VIN:

### A. Detección Inteligente de Mercado (Enrutador WMI)
En lugar de forzar al usuario a saber de dónde viene el auto, el módulo `wmi_detector.py` extrae los primeros 3 caracteres del VIN (World Manufacturer Identifier) y mediante diccionarios geográficos determina si el vehículo fue ensamblado o comercializado para el mercado de Norteamérica (USA/Canadá) o para el mercado Euro-Asiático (ej. Corea del Sur, Japón, Alemania).

### B. Enrutamiento a Proveedor Estratégico
Basado en lo anterior, el sistema consume el API de suscripción más adecuado para maximizar el margen de ganancia y la precisión de los datos:
- **Mercado Norteamericano:** Se enruta hacia **VinAudit** (`api.vinaudit.com`).
- **Mercado Coreano / Internacional:** Se enruta hacia **Vincario** (`api.vincario.com`).

### C. Sistema de Ahorro y Caché (Protección de Costos)
**Requisito Contractual:** Evitar pagar múltiples veces por un mismo reporte si distintos usuarios consultan el mismo VIN en un periodo corto de tiempo.
- **Funcionamiento:** Antes de gastar saldo en una llamada externa (Llamada Mayorista), el sistema busca en la Base de Datos Local (`VehiculoEstudio`). Si existe un reporte físico generado con menos de **30 días de antigüedad**, el sistema omite el API externa, y retorna de manera instantánea el reporte en Caché (Costo $0 - 100% Margen de Ganancia Institucional).

### D. Normalización de Datos y Generación Documental
Debido a que Vincario y VinAudit devuelven el JSON en esquemas completamente distintos, el módulo `normalizer.py` aplana y traduce la respuesta a un único modelo estándar de negocio.
Tras normalizar, se genera en caliente un **Acuse de Recibo en formato PDF** formal, que incluye los datos técnicos, título de salvamento, lecturas de odómetro, e insignias de agua de los proveedores y RACSA.

---

## 4. Dashboard Operativo y Monitoreo de Acuerdos de Nivel de Servicio (SLA)

Se desarrolló una interfaz de monitoreo accesible en `/api/v1/dashboard` exclusiva para el personal administrativo y de soporte técnico.

- **Indicador de Salud en Tiempo Real ("Sistema En Línea"):** 
  Ubicado en la esquina superior derecha del navbar, este indicador funciona como un **Health Check automatizado y asíncrono**. Un demonio en Javascript hace "ping" constante e invisible al endpoint `/health` cada 10 segundos.
  - El backend ejecuta una doble verificación asíncrona (`asyncio.gather`): primero evalúa la conectividad a la base de datos local SQLite, y simultáneamente dispara pings HTTP hacia los dominios maestros de **VinAudit (USA)** y **Vincario (Corea)** limitados por un timeout estricto de 3.0 segundos.
  - **Comportamiento Visual Semafórico:**
    - 🟢 **Verde ("Sistema En Línea"):** La base de datos local funciona y ambos proveedores externos respondieron al ping a tiempo.
    - 🟠 **Naranja ("Proveedores Lentos"):** La base de datos funciona, pero al menos uno de los proveedores internacionales tardó más de 3 segundos en responder o denegó la conexión. Alerta preventiva de lentitud externa.
    - 🔴 **Rojo ("Sistema Caído / Error BD"):** El motor local de SQLite se encuentra inaccesible, bloqueado o corrupto. Es el estado más crítico.
- **Métricas Contractuales:** Filtro de consultas por fecha (DD/MM/YYYY) que grafica cuántas peticiones totales ingresaron, cuántas representaron gasto real de factura externa y cuántas fueron ahorros directos por cachés.
- **Bitácora Oficial de Trazabilidad:** Un componente de lista inmutable que guarda el registro absoluto de cada consulta realizada (exitosa o fallida).
  - Incluye acceso directo en un click al `.pdf` emitido de cada transacción.
  - Ofrece una modalidad de **Auditoría Técnica (Ver Detalle)** para aislar códigos HTTP 400 y 500 arrojados por los proveedores, útiles para justificaciones de caída de línea mediante captura de la exepción y el Endpoint específico de la falla.
  - **Trazabilidad B2B y Auditoría IP:** El proxy enruta de manera automática la dirección de origen HTTP (`request.client.host`) y el ID del usuario desencriptado desde el Token JWT para inyectarlo directo a la bitácora, previniendo fuga de consultas en cuentas comerciales.
- **Exportación Contable CSV:** Un submódulo integrado al filtro histórico permite la extracción inmediata de toda la bitácora visible (filtrada por rangos dinámicos en UTC) hacia un formato de hoja de cálculo estándar separado por comas, listo para la conciliación manual de fin de mes o entrega de reportes a la Contraloría.

---

## 5. Esquema de Seguridad Integral

GlobalVIN ha sido blindado siguiendo las mejores prácticas para aplicaciones web expuestas a internet:

1. **Autenticación Basada en Tokens (JWT - RFC 7519):**
   - El sistema no usa sesiones de cookies vulnerables a CSRF. Toda petición al motor de consultas de VINs requiere un encabezado `Authorization: Bearer <token>`.
   - Los tokens son firmados criptográficamente mediante el algoritmo `HS256` utilizando una llave secreta de entorno (`SECRET_KEY`). Tienen tiempo de vida limitado configurable (`ACCESS_TOKEN_EXPIRE_MINUTES`).
2. **Encriptación de Contraseñas:**
   - Para generar tokens, los clientes deben tener un usuario registrado. Las contraseñas en Base de Datos jamás se guardan en texto plano; son "hasheadas" utilizando la librería criptográfica **Passlib con el algoritmo nativo `bcrypt`**.
3. **Mitigación de Abusos y Ataques DDoS (Rate Limiting):**
   - Se implementó la librería `slowapi` adherida al middleware principal de FastAPI.
   - Todo endpoint de la API está protegido contra ataques de fuerza bruta o inundaciones transaccionales no intencionadas, bloqueando peticiones (HTTP 429 Too Many Requests) que superen un umbral definido en memoria limitando solicitudes por dirección IP original del cliente.
4. **CORS (Cross-Origin Resource Sharing):**
   - El middleware solo permite conexiones explícitas provenientes de orígenes/dominios autorizados, denegando lecturas no deseadas desde scripts en navegadores de extraños.

---

## 6. Mantenimiento y Extensibilidad Futura

Para el mantenimiento del equipo de ingeniería institucional, se dejan previstas las siguientes directrices:

- **Migración a Base de Datos Enterprise:** Al utilizar `app.db.session` y las migraciones de `SQLAlchemy`, si los 3,000 reportes estimados mensuales exceden la carga en el futuro, no se requiere refactorizar ninguna lógica de negocio; basta con actualizar la URL `DATABASE_URL=postgresql+asyncpg://user:pass@host/db`.
- **Nuevo Proveedor Regional:** Si en el futuro RACSA adquiere un tercer proveedor (p. ej. para flota institucional en Centroamérica), basta con modificar la condición silogística en `app/services/wmi_detector.py` y crear un `provider_client.py` que herede la firma estructural base.
- **Integración DevOps:** El proyecto incluye un archivo estricto de `.gitignore` limpio, preparado para ser empaquetado como contenedor de Docker y ejecutado bajo un orquestador moderno (como Kubernetes o AWS ECS), escalando los contenedores de FastAPI horizontalmente gracias a su naturaleza asíncrona "Stateless".

---

## 7. Anexos: Referencia de API de Proveedores (Ejemplos JSON)

El sistema lidia internamente con dos esquemas muy diferentes que son "aplanados" (Normalizados) y guardados en SQLite. A continuación se muestran recortes de exactitud estructural de cómo ingresan los datos desde el exterior.

### A. VinAudit (Vehículos Mercado Estadounidense / Canadiense)

Basado en el endpoint formal de reportes extensos. Es capaz de delinear historial de kilometraje, subastas de aseguradoras y alertas graves.

```json
{
  "status": "success",
  "data": {
    "vin": "JTHBK1GG3E2131249",
    "attributes": {
      "make": "Lexus",
      "model": "ES",
      "year": "2014",
      "engine": "3.5L V6",
      "made_in": "Japan",
      "steering_type": "Rack & Pinion"
    },
    "titles": [
      {
        "state": "CA",
        "date": "2024-11-08",
        "meter": "102984",
        "meter_unit": "M",
        "current": true
      }
    ],
    "checks": [
      {
        "brander_name": "CALIFORNIA",
        "brand_title": "Salvage: Damage or Not Specified",
        "date": "2022-12-14",
        "brander_type": "State"
      }
    ],
    "salvage": [
      {
        "date": "2022-12-21",
        "type": "salvageAuction",
        "location": "ACE - Carson CA",
        "primary_damage": "Rear",
        "title_type": "Salvage certificate California"
      }
    ]
  }
}
```

### B. Vincario (Vehículos Mercado Coreano / Europeo)

Usado prioritariamente para descubrir características técnicas de chasis y especificaciones directas de ensambladora. El sistema aplica SHA1 dinámico para crear un `control_sum` en cada HTTP Request enviada.

```json
{
  "control_sum": "d41d8cd98f",
  "decode": [
    {
      "label": "Make",
      "value": "Kia"
    },
    {
      "label": "Model",
      "value": "Sorento"
    },
    {
      "label": "Model Year",
      "value": "2021"
    },
    {
      "label": "Plant Country",
      "value": "South Korea"
    },
    {
      "label": "Body",
      "value": "SUV"
    },
    {
      "label": "Engine Displacement (ccm)",
      "value": "2497"
    },
    {
      "label": "Fuel Type - Primary",
      "value": "Gasoline"
    },
    {
      "label": "Transmission",
      "value": "8-Speed Automatic"
    }
  ]
}
```
