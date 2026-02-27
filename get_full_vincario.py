import urllib.request
import json
import hashlib

API_KEY = "07388061bedf"
SECRET_KEY = "393729ddf8"
VIN = "KNAFU4A27A5377106".upper()
ID = "decode"

raw_string = f"{VIN}|{ID}|{API_KEY}|{SECRET_KEY}"
control_sum = hashlib.sha1(raw_string.encode('utf-8')).hexdigest()[:10]
url = f"https://api.vincario.com/3.2/{API_KEY}/{control_sum}/{ID}/{VIN}.json"

req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode('utf-8'))
    with open('full_vincario.json', 'w') as f:
        json.dump(data, f, indent=2)
