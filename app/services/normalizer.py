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

def normalize_vincario_response(raw_data: Dict[str, Any]) -> Tuple[EspecificacionesVehiculo, DetalleEstudio, bool]:
    """
    Transforms Vincario (Korea/Intl) JSON into the required format.
    The data comes in a 'Decode' array with 'label' and 'value'.
    """
    data = raw_data.get("data", {})
    decode_list = data.get("Decode", [])
    
    # Convert list of dicts to a fast lookup dict
    decode_dict = {item.get("label", ""): item.get("value", "") for item in decode_list if isinstance(item, dict)}

    meta = EspecificacionesVehiculo(
        marca=decode_dict.get("Make"),
        modelo=decode_dict.get("Model"),
        anio=decode_dict.get("Model Year"),
        fabricacion=decode_dict.get("Plant Country", decode_dict.get("Manufacturer Address")),
        motor=f"{decode_dict.get('Engine Displacement (ccm)', '')}cc {decode_dict.get('Fuel Type - Primary', '')}".strip(),
        categoria=decode_dict.get("Body"),
        estilo=decode_dict.get("Transmission")
    )

    detalle = DetalleEstudio()
    
    # Vincario's basic decode endpoint might not bring full accident history
    # If using their advanced endpoints, map them here later
    # For now, initialize empty lists
    es_sin_registros = True

    return meta, detalle, es_sin_registros

def normalize_provider_data(provider: str, raw_data: Dict[str, Any]) -> Tuple[EspecificacionesVehiculo, DetalleEstudio, bool]:
    if provider == "Vincario":
        return normalize_vincario_response(raw_data)
    else:
        return normalize_vinaudit_response(raw_data)
