import httpx
import asyncio
from typing import Dict, Any, Tuple
from app.core.config import settings
from app.services.wmi_detector import get_vehicle_origin_from_vin

async def fetch_vinaudit_data(vin: str) -> Dict[str, Any]:
    """
    Integration for VinAudit API (United States).
    """
    api_key = settings.VINAUDIT_API_KEY
    if not api_key or api_key.startswith("dummy"):
        # Not configured properly, fallback to mock
        await asyncio.sleep(1.0)
        return {
            "success": True,
            "vehicle": {
                "make": "FORD MOCK",
                "model": "F-150 MOCK",
                "year": 2021,
                "country": "United States",
                "engine": "3.5L V6 Turbo",
            },
            "history": {
                "accidents": [],
                "salvage": False,
                "theft": False,
                "liens": 0
            }
        }

    url = f"https://marketvalue.vinaudit.com/getmarketvalue.php"
    params = {
        "key": api_key,
        "vin": vin,
        "format": "json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=15.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            # Fallback to mock data on error for testing purposes
            return {"success": False, "error": str(e), "vehicle": {"make": "ERROR"}, "history": {}}

import hashlib

async def fetch_vincario_data(vin: str) -> Dict[str, Any]:
    """
    Integration for Vincario API (International/Korea).
    """
    api_key = settings.VINCARIO_API_KEY
    secret_key = settings.VINCARIO_SECRET_KEY
    
    if not api_key or not secret_key or api_key.startswith("dummy"):
        # Not configured properly, fallback to mock
        await asyncio.sleep(1.0)
        return {"status": "mock", "data": {"error": False, "Decode": [{"label": "Make", "value": "MOCK KOREAN VINCARIO"}]}}

    # Vincario requires VIN in uppercase
    vin_upper = vin.upper()
    endpoint_id = "decode"
    
    # Control sum: first 10 characters of SHA1 hash of: VIN|ID|API key|Secret key
    raw_string = f"{vin_upper}|{endpoint_id}|{api_key}|{secret_key}"
    control_sum = hashlib.sha1(raw_string.encode('utf-8')).hexdigest()[:10]

    url = f"https://api.vincario.com/3.2/{api_key}/{control_sum}/{endpoint_id}/{vin_upper}.json"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            data = response.json()
            
            # Vincario returns "error": true or false
            if data.get("error"):
                # Bad VIN or validation failure
                return {"status": "error_fallback", "error": str(data), "data": {}}
                
            response.raise_for_status()
            return {"status": "success", "data": data}
            
        except httpx.HTTPError as e:
            # Fallback to mock data on HTTP failure
            return {"status": "error_fallback", "error": str(e), "data": {}}

async def fetch_vinaudit_data(vin: str) -> Dict[str, Any]:
    """
    Integration for VinAudit API (USA).
    """
    api_key = settings.VINAUDIT_API_KEY
    if not api_key or api_key.startswith("dummy"):
        await asyncio.sleep(1.0)
        return {"status": "mock", "data": {"vehicle": {"make": "MOCK USA VEHICLE"}}}

    # VinAudit standard endpoint
    url = f"https://api.vinaudit.com/v2/pullreport"
    params = {"key": api_key, "vin": vin, "format": "json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"status": "error_fallback", "error": str(e), "data": {}}

async def orchestrate_vin_search(vin: str) -> Tuple[Dict[str, Any], str]:
    """
    Routes the VIN to the appropriate provider based on its origin (e.g. 1st char).
    """
    # Ex: 1, 4, 5 = USA; K = Korea
    # If the VIN starts with K, route to Vincario (Korea)
    # If it starts with 1, 4, 5, route to VinAudit (USA)
    if vin.upper().startswith("K"):
        data = await fetch_vincario_data(vin)
        return data, "Vincario"
    else:
        # Defaulting to VinAudit for USA and others for this business case
        data = await fetch_vinaudit_data(vin)
        return data, "VinAudit"
