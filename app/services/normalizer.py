from typing import Dict, Any, Tuple
from app.schemas.vehiculo import (
    EspecificacionesVehiculo,
    DetalleEstudio,
    RegistroAccidente,
    RegistroRobo,
    RegistroSeguro,
    ComprobacionProblemas
)

def normalize_vinaudit_response(raw_data: Dict[str, Any]) -> Tuple[EspecificacionesVehiculo, DetalleEstudio, bool]:
    """
    Transforms VinAudit JSON into the required format.
    Returns: (EspecificacionesVehiculo, DetalleEstudio, es_estudio_sin_registros)
    """
    vehicle_info = raw_data.get("vehicle", {})
    history_info = raw_data.get("history", {})

    meta = EspecificacionesVehiculo(
        marca=vehicle_info.get("make"),
        modelo=vehicle_info.get("model"),
        anio=vehicle_info.get("year"),
        categoria=vehicle_info.get("trim"),
        fabricacion=vehicle_info.get("country"),
        motor=vehicle_info.get("engine"),
        estilo=vehicle_info.get("body_style"),
    )

    detalle = DetalleEstudio()
    
    # Fake mapping some accidents if they exist
    for acc in history_info.get("accidents", []):
        detalle.registrosDeAccidentes.append(RegistroAccidente(
            fecha="N/A", entidadInformante="N/A"
        ))
        
    if history_info.get("salvage", False):
        detalle.chatarraSalvamentoSeguros.append(RegistroSeguro(
            fecha="N/A", tipoDeDano="Salvage", entidadInformante="Insurance"
        ))
        
    if history_info.get("theft", False):
        detalle.registrosDeRobos.append(RegistroRobo(
            tipoDeRegistro="Theft", fechaDeRobo="N/A"
        ))

    # Determine if it's a completely clean record
    es_sin_registros = not (
        len(detalle.registrosDeAccidentes) > 0 or 
        len(detalle.chatarraSalvamentoSeguros) > 0 or 
        len(detalle.registrosDeRobos) > 0 or
        history_info.get("liens", 0) > 0
    )

    return meta, detalle, es_sin_registros

def normalize_carapis_response(raw_data: Dict[str, Any]) -> Tuple[EspecificacionesVehiculo, DetalleEstudio, bool]:
    """
    Transforms CarApis (Encar) JSON into the required format.
    """
    # NOTE: Since the real endpoint is currently returning 404, we don't know the exact structure
    # of the CarApis JSON. We will adapt this mapping once support provides the correct endpoint and we see a real payload.
    # For now, we will map based on our mock fallback in the provider_client.
    data = raw_data.get("data", {})
    specs = data.get("specs", {})
    summary = data.get("history_summary", {})

    meta = EspecificacionesVehiculo(
        marca=specs.get("brand"),
        modelo=specs.get("model_name"),
        anio=specs.get("production_year"),
        fabricacion=specs.get("origin"),
        motor=specs.get("engine_type"),
    )

    detalle = DetalleEstudio()
    
    if summary.get("has_accident_history", False):
        detalle.registrosDeAccidentes.append(RegistroAccidente(fecha="N/A", entidadInformante="CarApis Source"))
        
    if summary.get("total_loss_reported", False):
        detalle.chatarraSalvamentoSeguros.append(RegistroSeguro(fecha="N/A", tipoDeDano="Total Loss"))
        
    if summary.get("theft_reported", False):
        detalle.registrosDeRobos.append(RegistroRobo(tipoDeRegistro="Theft", fechaDeRobo="N/A"))

    es_sin_registros = not (
        len(detalle.registrosDeAccidentes) > 0 or 
        len(detalle.chatarraSalvamentoSeguros) > 0 or 
        len(detalle.registrosDeRobos) > 0
    )

    return meta, detalle, es_sin_registros

def normalize_provider_data(provider: str, raw_data: Dict[str, Any]) -> Tuple[EspecificacionesVehiculo, DetalleEstudio, bool]:
    if provider == "CarApis":
        return normalize_carapis_response(raw_data)
    else:
        return normalize_vinaudit_response(raw_data)
