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
En lugar de forzar al usuario a saber de dónde viene el auto, el módulo `wmi_detector.py` toma los **primeros 3 caracteres** del VIN alfanumérico. Este bloque se conoce internacionalmente como el **WMI** (World Manufacturer Identifier).
- El sistema cuenta con un diccionario interno geográfico. Si el VIN comienza con ciertas letras (como la **"K"** para Corea del Sur, p. ej. `KNA` para KIA o `KMH` para Hyundai), identifica inmediatamente que la manufactura es asiática.
- Si comienza con los números **1, 4 o 5** (Estados Unidos), **2** (Canadá) o **3** (México), el sistema detecta de fábrica que el flujo histórico de este auto está centralizado en el estándar americano.

### B. Enrutamiento a Proveedor Estratégico (Optimización de Costos)
Una vez resuelto el mapa geográfico por el WMI, el sistema toma una decisión transaccional para maximizar la calidad del reporte y minimizar el gasto:
- **Mercado Norteamericano (VINs 1-5):** La consulta se enruta hacia el API de **VinAudit** (`api.vinaudit.com`). Las aseguradoras y el NMVTIS (Títulos Salvage) de USA están directamente centralizados aquí.
- **Mercado Coreano / Internacional (VINs K*, J*, W*):** La consulta se enruta a través de la red Europea de **Vincario** (`api.vincario.com`), la cual funciona mediante la inyección de hashes SHA1. Si usáramos VinAudit para un KIA importado directamente desde Seúl sin pasar por USA, el saldo se gastaría y el reporte vendría vacío.

### C. Sistema de Ahorro y Caché (Protección de Costos frente a Peticiones Repetidas)
**Requisito Contractual:** Evitar pagar múltiples veces por un mismo reporte si distintos usuarios o interfaces consultan el mismo VIN en un periodo corto de tiempo.
- **Funcionamiento (Hit de Caché):** Cada vez que ingresa una petición, el sistema busca en la Base de Datos Local (`VehiculoEstudio` o `Trazabilidad`) usando el VIN exacto. Si encuentra que ya se emitió un reporte para ese vehículo hace **menos de 30 días**, el orquestador aborta inmediatamente cualquier intento de conexión a VinAudit o Vincario.
- **Manejo Financiero y Operativo:** En lugar de hacer una nueva "Llamada Mayorista" cobrable, el sistema simplemente recicla el último JSON normalizado de la base de datos y le devuelve al usuario instantáneamente el reporte en memoria (o la URL del PDF pre-existente). Esto representa una transacción de Costo $0 para RACSA, generando un 100% de margen de ganancia si se le factura a ese cliente B2B.

### D. Normalización de Datos y Generación Documental (PDF Automático)
Debido a que Vincario y VinAudit devuelven el JSON en esquemas completamente distintos, el módulo `normalizer.py` aplana y traduce la respuesta original a un único modelo estándar de negocio.
- **Creación en Caliente del PDF:** Tras normalizar los datos en Pydantic, el backend inyecta las variables en una plantilla HTML semántica prediseñada mediante el motor Jinja2.
- **Motor WebKit:** Luego, se invoca a la librería base `wkhtmltopdf` (alojada en el sistema operativo del servidor). Esta herramienta renderiza de forma invisible el HTML como si fuera un navegador web real (WebKit engine) y lo "imprime" en un archivo PDF binario vectorial.
- **Resultado Final:** Se entrega un Acuse de Recibo en formato PDF, el cual incluye fotografías, datos técnicos, títulos de salvamento (NMVTIS estadounidense), incidentes reportados, y las insignias de agua y seguridad (logos) de RACSA y el respectivo proveedor de datos. Este archivo se guarda de forma persistente estáticamente para ser descargado o enlazado desde un S3 sin necesidad de reconstruirse.

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
