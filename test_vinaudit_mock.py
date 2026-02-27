import asyncio
import json
from app.services.provider_client import orchestrate_vin_search
from app.services.normalizer import normalize_provider_data

async def main():
    vin = "1VXBR12EXCP901214"
    print(f"Testing VIN: {vin}")
    
    # 1. Fetch data
    raw_data, provider_name = await orchestrate_vin_search(vin)
    print(f"\nProvider Selected: {provider_name}")
    print(f"Raw Status: {raw_data.get('status')}")
    
    # 2. Normalize
    if raw_data.get("status") == "success":
        meta, detalle, clean = normalize_provider_data(provider_name, raw_data)
        print("\n--- Normalized Data ---")
        print(f"Clean Record (es_sin_registros): {clean}")
        print("\nMeta:")
        print(meta.model_dump_json(indent=2))
        print("\nDetalle:")
        print(detalle.model_dump_json(indent=2))
    else:
        print("Failed to fetch data properly.")
        print(raw_data)

if __name__ == "__main__":
    asyncio.run(main())
