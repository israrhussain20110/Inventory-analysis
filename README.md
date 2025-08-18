# Inventory Forecasting Project

## Description

This project provides an inventory forecasting and management system using FastAPI and Prophet. It allows for uploading inventory and sales data, calculating various inventory metrics, and forecasting future inventory needs.

## Setup and Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/inventory-forecasting.git
    cd inventory-forecasting
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    Create a `.env` file in the root directory and add your MongoDB URI:

    MONGO_URI="mongodb://localhost:27017/"

## How to Run

1. **Start MongoDB:** Ensure your MongoDB instance is running.
2. **Run the FastAPI application:**

    ```bash
    uvicorn app.main:app --reload
    ```

    The API will be accessible at `http://127.0.0.1:8000`.

## API Endpoints

- `/docs`: Interactive API documentation (Swagger UI).
- `/upload/{collection_name}` (POST): Upload CSV data to a specified MongoDB collection.
- `/status` (GET): Check the data loading status.
- `/inventory/metrics` (GET): Get inventory metrics for a product.
- `/inventory/slow_movers` (GET): Get a list of slow-moving and obsolete items.
- `/inventory/stockouts` (GET): Get stockout history and rates.
- `/inventory/stockouts/heatmap` (GET): Get data for a stockout heatmap.
- `/inventory/slow_movers/report` (GET): Download a CSV report of slow-moving and obsolete items.
- `/forecasting/predict` (POST): Predict future inventory based on historical data.
- `/metrics/all-metrics` (POST): Get all metrics for a specific store and product.
