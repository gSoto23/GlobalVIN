import httpx
import asyncio
import json

async def test_globalvin_api():
    url = "http://localhost:8000/api/v1/vehiculos/estudios"
    
    # 1. First we need to get a token
    # For now, since auth is mock/in-memory, we can pass any string 
    # if the JWT middleware is not fully enforcing signatures yet, 
    # OR we can just bypass if we are testing locally.
    # Assuming auth is required, let's provide a dummy Bearer
    headers = {
        "Authorization": "Bearer dummy_test_token"
    }

    # 2. Test payload for a GET request
    params = {
        "identificacion": "KNA12345678TESTVIN", # KNA = Korea
        "tipoIdentificacion": "VIN"
    }

    print(f"Enviando GET a {url} con VIN {params['identificacion']}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, headers=headers, timeout=20.0)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ Metadatos Recibidos:")
                print(json.dumps(data.get('especificacionesVehiculo', {}), indent=2))
                
                # Check if PDF base64 is present
                pdf_info = data.get('pdf', {})
                if 'content' in pdf_info:
                    print(f"\n✅ PDF generado. Hash SHA-256: {pdf_info.get('hash')}")
            else:
                print("\n❌ Error en la respuesta:")
                print(json.dumps(response.json(), indent=2))
        except Exception as e:
            print(f"Error de red: {e}")

if __name__ == "__main__":
    asyncio.run(test_globalvin_api())
