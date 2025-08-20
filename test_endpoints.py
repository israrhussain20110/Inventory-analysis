import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

endpoints = [
    "/inventory/metrics",
    "/inventory/metrics?product_id=P0001",
    "/inventory/metrics?period=daily",
    "/inventory/slow_movers",
    "/inventory/stockouts",
    "/inventory/stockouts?product_id=P0001",
    "/inventory/stockouts/heatmap",
    "/inventory/stockouts/heatmap?product_id=P0001",
    "/inventory/slow_movers/report"
]

for endpoint in endpoints:
    url = BASE_URL + endpoint
    try:
        with urllib.request.urlopen(url) as response:
            print(f"Request to {url} successful")
            if 'report' in endpoint:
                print("Report content omitted.")
            else:
                data = response.read()
                print(json.loads(data))
    except Exception as e:
        print(f"Request to {url} failed: {e}")
