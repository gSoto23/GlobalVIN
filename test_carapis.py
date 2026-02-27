import httpx
import asyncio
import json

API_KEY = "car__FBHhPP3YHzDsz7AazvTfXaFustK6IInwuR6uTUm1LGQ"
BASE_URL = "https://api.carapis.com"

async def test_api():
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # Testing the search endpoint
    search_params = {
        "brand": "Hyundai",
        "limit": 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print(f"Sending GET request to {BASE_URL}/encar/vehicles")
            
            response = await client.get(
                f"{BASE_URL}/encar/vehicles", 
                headers=headers,
                params=search_params,
                timeout=30.0 
            )
            
            print("Status Code:", response.status_code)
            
            try:
                # Pretty print JSON response
                print("JSON Response:")
                print(json.dumps(response.json(), indent=2))
            except json.JSONDecodeError:
                print("Raw Response:", response.text)
                
        except Exception as e:
            print("An error occurred:", e)

if __name__ == "__main__":
    asyncio.run(test_api())
