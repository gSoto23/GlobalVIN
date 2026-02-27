from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class EspecificacionesVehiculo(BaseModel):
    vin: Optional[str] = Field(None, description="1.1.1 El número de identificación completo del vehículo")
    anio: Optional[int] = Field(None, description="1.1.2 El año calendario en el que se fabricó el vehículo")
    marca: Optional[str] = Field(None, description="1.1.3 Fabricante o el nombre comercial de este vehículo")
    modelo: Optional[str] = Field(None, description="1.1.4 El diseño particular o la versión de este vehículo")
    categoria: Optional[str] = Field(None, description="1.1.5 El estilo o submodelo dentro del modelo actual")
    motor: Optional[str] = Field(None, description="1.1.6 El tamaño y tipo del motor de combustión")
    estilo: Optional[str] = Field(None, description="1.1.7 La clase y el tipo de diseño general")
    fabricacion: Optional[str] = Field(None, description="1.1.8 País de origen donde se fabricó el vehículo")
    tipoDeManubrio: Optional[str] = Field(None, description="1.1.9 Los componentes o sistema de dirección")
    sistemaDeFrenos: Optional[str] = Field(None, description="1.1.10 El sistema de seguridad del automóvil")
    tamanoDelTanque: Optional[str] = Field(None, description="1.1.11 La cantidad total de combustible")
    alturaTotal: Optional[str] = Field(None, description="1.1.12 La medida general, de arriba a abajo")
    longitudTotal: Optional[str] = Field(None, description="1.1.13 La medición general del lado más largo")
    anchoTotal: Optional[str] = Field(None, description="1.1.14 La medida general del grosor del vehículo")
    asientosEstandar: Optional[int] = Field(None, description="1.1.15 El número prescrito de asientos disponibles")
    kilometrajeEnCarretera: Optional[str] = Field(None, description="1.1.16 Eficiencia de combustible estimada (autopista)")
    kilometrajeEnLaCiudad: Optional[str] = Field(None, description="1.1.17 Eficiencia de combustible estimada (ciudad)")

class RegistroTitulo(BaseModel):
    fecha: Optional[str] = Field(None, description="1.2.1 La fecha de emisión del título")
    tipo: Optional[str] = Field(None, description="1.2.2 El estado actual del propietario del título")
    kilometraje: Optional[str] = Field(None, description="1.2.3 El número de millas cubiertas")
    vin: Optional[str] = Field(None, description="1.2.4 El número de identificación asociado")
    estadoProvincia: Optional[str] = Field(None, description="1.2.5 El nombre de la provincia que emite el título")

class RegistroSeguro(BaseModel):
    fecha: Optional[str] = Field(None, description="1.3.1 La fecha en que la entidad adquirió el vehículo")
    entidadInformante: Optional[str] = Field(None, description="1.3.2 La agencia que informó este registro")
    tipoDeDano: Optional[str] = Field(None, description="1.3.3 El tipo de daño sufrido por el vehículo")
    disposicion: Optional[str] = Field(None, description="1.3.4 El estado de venta del vehículo")
    destinadoALaExportacion: Optional[bool] = Field(None, description="1.3.5 Si este vehículo fue destinado a la exportación")

class RegistroAccidente(BaseModel):
    fecha: Optional[str] = Field(None, description="1.4.1 La fecha en que ocurrió el accidente")
    entidadInformante: Optional[str] = Field(None, description="1.4.2 La agencia que informó el accidente")
    numeroReportado: Optional[str] = Field(None, description="1.4.3 El ID del informe del accidente")
    descripcionDelVehiculo: Optional[str] = Field(None, description="1.4.4 Descripción del vehículo en el informe")
    danoEstimado: Optional[str] = Field(None, description="1.4.5 La valoración aproximada del daño")
    velocidadEstimada: Optional[str] = Field(None, description="1.4.6 La velocidad aproximada del vehículo")
    areaDeImpacto: Optional[str] = Field(None, description="1.4.7 La parte del vehículo donde se dañó")
    companiaDeSeguros: Optional[str] = Field(None, description="1.4.8 Compañía de seguros que cubrió los daños")

class RegistroRobo(BaseModel):
    tipoDeRegistro: Optional[str] = Field(None, description="1.5.1 El registro especificado del vehículo")
    fechaDeRobo: Optional[str] = Field(None, description="1.5.2 La fecha en que este vehículo fue robado")
    fechaDeRecuperacion: Optional[str] = Field(None, description="1.5.3 La fecha en que se recuperó")
    estadoDenunciadoPorRobo: Optional[str] = Field(None, description="1.5.4 Estado que informó el robo")
    estadoDeRobo: Optional[str] = Field(None, description="1.5.5 El estado actual del robo")
    anioDelVehiculo: Optional[str] = Field(None, description="1.5.6 El año calendario de fabricación")
    marcaDelVehiculo: Optional[str] = Field(None, description="1.5.7 El fabricante o nombre comercial")
    fuente: Optional[str] = Field(None, description="1.5.8 La agencia donde se obtiene el registro")

class RegistroEmbargoExportacion(BaseModel):
    tipoDeRegistro: Optional[str] = Field(None, description="1.6.1 El tipo de registro especificado")
    fecha: Optional[str] = Field(None, description="1.6.2 La fecha en que ocurrió la línea, embargo o exportación")
    titularDelGravamen: Optional[str] = Field(None, description="1.6.3 Compañía financiera con gravamen")
    fechaDeEmbargo: Optional[str] = Field(None, description="1.6.4 Fecha en que se realizó el embargo")
    provincia: Optional[str] = Field(None, description="1.6.5 Provincia donde fue confiscado/exportado")
    vin: Optional[str] = Field(None, description="1.6.6 El número de identificación asociado")

class RegistroVenta(BaseModel):
    fecha: Optional[str] = Field(None, description="1.7.1 Fecha en que fue puesto a la venta")
    vendedor: Optional[str] = Field(None, description="1.7.2 Entidad que vendió el vehículo")
    precioDeListado: Optional[str] = Field(None, description="1.7.3 Precio listado")
    kilometrajeDelVehiculo: Optional[str] = Field(None, description="1.7.4 Millaje total al momento de venta")

class ComprobacionProblemas(BaseModel):
    registroDeDanosPorInundacion: bool = False
    registroDeDanosPorIncendio: bool = False
    registroDeDanosPorGranizo: bool = False
    registroDeDanosPorAguaSalada: bool = False
    registroDeVandalismo: bool = False
    registroDelVehiculoKit: bool = False
    registroDeDesmantelado: bool = False
    registroDeBasura: bool = False
    registroDeReconstruccion: bool = False
    registroDeReconstruido: bool = False
    registroDeSalvamentoDenoONoEspecificado: bool = False
    registroDelVehiculoDePrueba: bool = False
    registroDeReacondicionado: bool = False
    registroDeVehiculoDeColision: bool = False
    registroDeRetencionDeSalvamento: bool = False
    registroDelVehiculoDeTaxi: bool = False
    registroDelVehiculoPolicial: bool = False
    registroDelVehiculoDeTaxiOriginal: bool = False
    registroDelVehiculoPolicialOriginal: bool = False
    registroDelVehiculoRemanufacturado: bool = False
    registroDeDevolucionDeLaGarantia: bool = False
    registroDeAntiguedades: bool = False
    registroDeClasico: bool = False
    registroDelVehiculoAgricola: bool = False
    registroDelVehiculoDeRegistro: bool = False
    registroDeStreetRod: bool = False
    elVehiculoContieneVinReemitido: bool = False
    registroDeReplica: bool = False
    registroDeTotalizado: bool = False
    registroDelPropietarioRetenido: bool = False
    registroDeBonosPublicados: bool = False
    registroDeCopiaDeMemorando: bool = False
    registroDePiezasUnicamente: bool = False
    registroDeRoboRecuperado: bool = False
    registroDeGravamenNoRevelado: bool = False
    registroDePropietarioAnteriorDetenido: bool = False
    registroDeNoConformidadDelVehiculoSinCorregir: bool = False
    registroDeNoConformidadDelVehiculoCorregido: bool = False
    registroDelDefectoDeSeguridadDelVehiculoSinCorregir: bool = False
    registroDeDefectoDeSeguridadDelVehiculoCorregido: bool = False
    registroDeVinReemplazado: bool = False
    registroDeRecompraDelFabricante: bool = False
    registroDelAntiguoVehiculoDeAlquiler: bool = False
    registroDeSalvamentoRobado: bool = False
    registroDeSalvamentoRazonesQueNoSeanDanosORobo: bool = False
    registroDeDanosRevelados: bool = False
    registroDeNoReparableReparadoAnterior: bool = False
    registroDeAplastado: bool = False
    registroDelOdometroReal: bool = False
    registroDelOdometroNoActual: bool = False
    registroDelOdometroManipulacionVerificada: bool = False
    registroDelOdometroExentoDeDiuvolgacion: bool = False
    registroDelOdometroExcedeLimitesMecanicos: bool = False
    registroDelOdometroPuedeModificarse: bool = False
    registroDelOdometroReemplazado: bool = False
    registroDelOdometroLecturaEnMomentoDeRenovacion: bool = False
    registroDeOdometroDiscrepancia: bool = False
    registroDelOdometroTituloDeLaDivisionDeLlamadas: bool = False
    registroDelOdometroExcedeLosLimitesMecanicosRectificados: bool = False

class RecursosSuplementarios(BaseModel):
    recomendacion: Optional[str] = Field(None, description="1.9.1 Busca información de recuperación")
    requerimientos: Optional[str] = Field(None, description="1.9.2 Requerimientos de la herramienta")
    fuente: Optional[str] = Field(None, description="1.9.3 NHTSA")

class DetalleEstudio(BaseModel):
    registrosDeTitulos: List[RegistroTitulo] = []
    chatarraSalvamentoSeguros: List[RegistroSeguro] = []
    registrosDeAccidentes: List[RegistroAccidente] = []
    registrosDeRobos: List[RegistroRobo] = []
    registrosDeEmbargoExportacion: List[RegistroEmbargoExportacion] = []
    registrosDeVenta: List[RegistroVenta] = []
    comprobacionDeProblemas: Optional[ComprobacionProblemas] = None
    recursosSuplementarios: Optional[RecursosSuplementarios] = None
    
    model_config = ConfigDict(extra="allow")

class PdfInfo(BaseModel):
    content: Optional[str] = None
    tamañoBytes: Optional[int] = None
    hash: Optional[str] = None
    fechaGeneracion: Optional[datetime] = None
    yaFacturadoPreviamente: bool = False

class EstudioBaseResponse(BaseModel):
    tipoIdentificacion: str = Field(..., description="VIN, CHASIS, SERIE")
    identificacion: str
    tieneEstudios: bool
    ultimaFechaEstudio: Optional[datetime] = None

class EstudioCompletoResponse(EstudioBaseResponse):
    esEstudioSinRegistros: bool = False
    especificacionesVehiculo: Optional[EspecificacionesVehiculo] = None
    detalleEstudio: Optional[DetalleEstudio] = None
    pdf: Optional[PdfInfo] = None
