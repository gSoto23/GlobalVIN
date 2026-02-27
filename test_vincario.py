import urllib.request
import json
import hashlib

# Vincario Credentials
API_KEY = "07388061bedf"
SECRET_KEY = "393729ddf8"

# Test VIN (Using a standard test VIN or KNA dummy)
# Vincario requires VIN to be uppercase
VIN = "KNAFU4A27A5377106".upper()
# Or we can test with a known good VIN if requested

ID = "decode"

# Control sum: first 10 characters of SHA1 hash made of:
# VIN|ID|API key|Secret key
raw_string = f"{VIN}|{ID}|{API_KEY}|{SECRET_KEY}"
control_sum = hashlib.sha1(raw_string.encode('utf-8')).hexdigest()[:10]

url = f"https://api.vincario.com/3.2/{API_KEY}/{control_sum}/{ID}/{VIN}.json"

print(f"Testing Vincario URL: {url}")
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as response:
        print(f"Status: {response.status}")
        data = json.loads(response.read().decode('utf-8'))
        print(json.dumps(data, indent=2))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
