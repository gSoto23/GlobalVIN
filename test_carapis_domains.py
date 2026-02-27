import urllib.request
import json

domains = ["api.carapis.com", "new.carapis.com", "carapis.com"]
path = "/apix/data_encar_api/brands/"
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-ID,en;q=0.9,ru-ID;q=0.8,ru;q=0.7,id;q=0.6",
    "dnt": "1",
    "origin": "https://new.carapis.com",
    "referer": "https://new.carapis.com/",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "x-api-key": "car__Rz4dne3fhmRYaemx7Il27lydi7fbq1EdbMrPooY5yc"
}

for domain in domains:
    url = f"https://{domain}{path}"
    print(f"Testing {url}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"  Status: {response.status}")
            print(f"  Response: {response.read().decode('utf-8')[:100]}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error: {e.code}")
    except Exception as e:
        print(f"  Error: {e}")
