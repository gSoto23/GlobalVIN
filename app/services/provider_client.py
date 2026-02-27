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

async def fetch_carapis_data(vin: str) -> Dict[str, Any]:
    """
    Integration for CarApis (Encar) API (South Korea).
    """
    api_key = settings.CARAPIS_API_KEY
    if not api_key or api_key.startswith("dummy"):
        # Not configured properly, fallback to mock to prevent crashing
        await asyncio.sleep(1.0)
        return {"status": "mock", "data": {"history_summary": {"has_accident_history": True}, "specs": {"brand": "MOCK KOREAN"}}}

    # According to new Telegram discovery: https://api2.carapis.com/apix/data_encar_api/vehicles/{vin}/
    url = f"https://api2.carapis.com/apix/data_encar_api/vehicles/{vin}/"
    headers = {
        "x-api-key": api_key,
        "accept": "application/json"
    }
    
    # We no longer pass car_no as a query parameter because it is now in the path
    params = {}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            
            # If CarApis returns 404 due to the current Cloudflare issue, we catch it
            if response.status_code == 404:
                return {"status": "mock_fallback_404", "data": {"history_summary": {"has_accident_history": False}, "specs": {"brand": "CARAPIS 404 MOCK"}}}
                
            response.raise_for_status()
            
            # Since data format will be different, we should return the raw json.
            # Warning: normalizer needs to adapt to the exact JSON structure once CarApis works.
            return response.json()
            
        except httpx.HTTPError as e:
            # Fallback to mock data for now so the user can test the API flow
            return {"status": "error_fallback", "error": str(e), "data": {"history_summary": {}, "specs": {"brand": "ERROR MOCK"}}}

async def orchestrate_vin_search(vin: str) -> Tuple[Dict[str, Any], str, str]:
    """
    Determines the origin, calls the correct provider, and returns:
    (raw_provider_data, provider_name, raw_pdf_content)
    """
    origin = get_vehicle_origin_from_vin(vin)
    
    if origin == "South Korea":
        data = await fetch_carapis_data(vin)
        provider = "CarApis"
        # Mocking a PDF generation/fetch
        # In reality, the provider might return a PDF link we have to download
        pdf_content = "JVBERi0xLjQKJ_MOCK_PDF_CONTENT_KOREA_..." 
    else:
        # Defaulting to US provider (VinAudit) for 'United States' or 'Other'
        data = await fetch_vinaudit_data(vin)
        provider = "VinAudit"
        pdf_content = "JVBERi0xLjQKJ_MOCK_PDF_CONTENT_USA_..."

    return data, provider, pdf_content
