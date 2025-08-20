import urllib.request
import json
import subprocess
import time
import os
import sys

# Add project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

process = None

try:
    # Start the FastAPI application in a subprocess
    print("Starting FastAPI application...")
    process = subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    time.sleep(5) # Give the server some time to start

    print("Running tests...")
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

finally:
    if process:
        print("Stopping FastAPI application...")
        process.terminate()
        process.wait()
        # Print the captured output from the FastAPI application
        print("\n--- FastAPI Application Output ---")
        for line in process.stdout:
            print(line, end='')
        print("----------------------------------")