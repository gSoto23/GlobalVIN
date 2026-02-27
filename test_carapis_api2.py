import urllib.request
import json

url = "https://api2.carapis.com/apix/data_encar_api/brands/"
headers = {
    "x-api-key": "car__Rz4dne3fhmRYaemx7Il27lydi7fbq1EdbMrPooY5yc",
    "accept": "application/json"
}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print(response.read().decode('utf-8')[:500])
except Exception as e:
    print(f"Error: {e}")
