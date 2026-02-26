from typing import Dict, Any, Tuple
from app.schemas.vehiculo import MetadatosVehiculo, DetalleEstudio

def normalize_vinaudit_response(raw_data: Dict[str, Any]) -> Tuple[MetadatosVehiculo, DetalleEstudio, bool]:
    """
    Transforms VinAudit JSON into the required format.
    Returns: (MetadatosVehiculo, DetalleEstudio, es_estudio_sin_registros)
    """
    vehicle_info = raw_data.get("vehicle", {})
    history_info = raw_data.get("history", {})

    meta = MetadatosVehiculo(
        marca=vehicle_info.get("make"),
        modelo=vehicle_info.get("model"),
        anio=vehicle_info.get("year"),
        version=vehicle_info.get("trim"),
        paisOrigen=vehicle_info.get("country"),
        tipoCombustible=vehicle_info.get("fuel_type"),
        motor=vehicle_info.get("engine"),
        tipoTransmision=vehicle_info.get("transmission"),
        tipoCarroceria=vehicle_info.get("body_style"),
    )

    detalle = DetalleEstudio(
        tieneAccidentesRegistrados=len(history_info.get("accidents", [])) > 0,
        tienePerdidaTotal=history_info.get("salvage", False),
        tieneRegistrosSubasta=history_info.get("auction_records", False),
        tieneGravamenes=history_info.get("liens", 0) > 0,
        tieneRegistrosRobo=history_info.get("theft", False)
    )

    # Determine if it's a completely clean record
    es_sin_registros = not (
        detalle.tieneAccidentesRegistrados or 
        detalle.tienePerdidaTotal or 
        detalle.tieneRegistrosRobo or
        detalle.tieneGravamenes
    )

    return meta, detalle, es_sin_registros

def normalize_carstat_response(raw_data: Dict[str, Any]) -> Tuple[MetadatosVehiculo, DetalleEstudio, bool]:
    """
    Transforms CarStat JSON into the required format.
    """
    data = raw_data.get("data", {})
    specs = data.get("specs", {})
    summary = data.get("history_summary", {})

    meta = MetadatosVehiculo(
        marca=specs.get("brand"),
        modelo=specs.get("model_name"),
        anio=specs.get("production_year"),
        paisOrigen=specs.get("origin"),
        motor=specs.get("engine_type"),
        colorExterior=specs.get("color"),
    )

    detalle = DetalleEstudio(
        tieneAccidentesRegistrados=summary.get("has_accident_history", False),
        tienePerdidaTotal=summary.get("total_loss_reported", False),
        tieneRegistrosSubasta=summary.get("auction_listings_found", 0) > 0,
        tieneRegistrosRobo=summary.get("theft_reported", False)
    )

    es_sin_registros = not (
        detalle.tieneAccidentesRegistrados or 
        detalle.tienePerdidaTotal or 
        detalle.tieneRegistrosRobo
    )

    return meta, detalle, es_sin_registros

def normalize_provider_data(provider: str, raw_data: Dict[str, Any]) -> Tuple[MetadatosVehiculo, DetalleEstudio, bool]:
    if provider == "CarStat":
        return normalize_carstat_response(raw_data)
    else:
        return normalize_vinaudit_response(raw_data)
