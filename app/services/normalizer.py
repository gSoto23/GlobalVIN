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
    data = raw_data.get("data", {})
    attributes = data.get("attributes", {})

    meta = EspecificacionesVehiculo(
        marca=attributes.get("make"),
        modelo=attributes.get("model"),
        anio=attributes.get("year"),
        categoria=attributes.get("trim"),
        fabricacion=attributes.get("made_in", attributes.get("country")),
        motor=attributes.get("engine"),
        estilo=attributes.get("style", attributes.get("body_style")),
    )

    detalle = DetalleEstudio()
    
    for acc in data.get("accidents", []):
        detalle.registrosDeAccidentes.append(RegistroAccidente(
            fecha=acc.get("date", "N/A"),
            entidadInformante=acc.get("source_name", "N/A")
        ))
        
    for salv in data.get("salvage", []):
        detalle.chatarraSalvamentoSeguros.append(RegistroSeguro(
            fecha=salv.get("date", "N/A"),
            tipoDeDano=salv.get("primary_damage", "Salvage"),
            entidadInformante=salv.get("sale_document", "Insurance")
        ))
        
    for jsi in data.get("jsi", []):
        detalle.chatarraSalvamentoSeguros.append(RegistroSeguro(
            fecha=jsi.get("date", "N/A"),
            tipoDeDano=jsi.get("record_type", "Junk/Salvage"),
            entidadInformante=jsi.get("brander_name", "N/A")
        ))
        
    for theft in data.get("thefts", []):
        detalle.registrosDeRobos.append(RegistroRobo(
            tipoDeRegistro=theft.get("record_type", "Theft"),
            fechaDeRobo=theft.get("date", "N/A")
        ))

    # Determine if it's a completely clean record
    es_sin_registros = not (
        len(detalle.registrosDeAccidentes) > 0 or 
        len(detalle.chatarraSalvamentoSeguros) > 0 or 
        len(detalle.registrosDeRobos) > 0 or
        len(data.get("lien", [])) > 0
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
