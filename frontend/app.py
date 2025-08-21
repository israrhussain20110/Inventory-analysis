from flask import Flask, render_template, request, jsonify
import requests
import json # Import json module

app = Flask(__name__)

FASTAPI_BASE_URL = "http://127.0.0.1:8000" # Changed to base URL for direct /predict access

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/<path:subpath>')
def api_proxy(subpath):
    # Construct the full URL for the FastAPI backend
    fastapi_url = f"{FASTAPI_BASE_URL}/inventory/{subpath}" # Adjusted for inventory routes
    
    # Include query parameters from the incoming request
    params = request.args

    try:
        response = requests.get(fastapi_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error proxying request to FastAPI: {e}")
        return jsonify({"error": "Failed to connect to backend API", "details": str(e)}), 500

@app.route('/forecast', methods=['POST'])
def get_forecast():
    data = request.get_json()
    store_id = data.get('store_id')
    product_id = data.get('product_id')
    granularity = data.get('granularity', 'monthly') # Default to monthly

    model_type = data.get('model_type', 'linear_regression') # Get model_type from request

    if not store_id or not product_id:
        return jsonify({"error": "Store ID and Product ID are required."}), 400

    fastapi_url = f"{FASTAPI_BASE_URL}/forecasting/predict" # Corrected call to /forecasting/predict

    payload = {
        "Store ID": store_id,  # Changed key
        "Product ID": product_id, # Changed key
        "granularity": granularity,
        "model_type": model_type # Include model_type in payload
    }

    try:
        response = requests.post(fastapi_url, json=payload)
        print(f"FastAPI response status code: {response.status_code}") # Debug print
        print(f"FastAPI response text: {response.text}") # Debug print
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast from FastAPI: {e}")
        return jsonify({"error": "Failed to fetch forecast", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)