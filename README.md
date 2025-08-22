# Inventory Forecasting Project

## Description

This project provides an advanced inventory forecasting and management system using FastAPI for the backend API and Flask for the frontend dashboard. It allows for uploading inventory and sales data, calculating various inventory metrics, and forecasting future inventory needs using multiple machine learning models (Linear Regression, Random Forest, and Support Vector Machines) at different time granularities (daily, monthly, quarterly, yearly).

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
    pip install scikit-learn  # New dependency for Random Forest and SVM
    ```

4. **Set up environment variables:**
    Create a `.env` file in the root directory and add your MongoDB URI:

    MONGO_URI="mongodb://localhost:27017/"

## How to Run

1. **Start MongoDB:** Ensure your MongoDB instance is running.

2. **Load Sample Data (Optional but Recommended):**
    Populate your MongoDB with sample data using the provided script:

    ```bash
    python scripts/load_data.py
    ```

3. **Run the FastAPI Backend Application:**

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

    The API will be accessible at `http://127.0.0.1:8000`.

4. **Run the Flask Frontend Application:**

    ```bash
    python frontend/app.py
    ```

    The frontend dashboard will be accessible at `http://127.0.0.1:5000/`.

## API Endpoints

- `/docs`: Interactive API documentation (Swagger UI).
- `/upload/{collection_name}` (POST): Upload CSV data to a specified MongoDB collection.
- `/status` (GET): Check the data loading status.
- `/inventory/metrics` (GET): Get inventory metrics for a product.
- `/inventory/slow_movers` (GET): Get a list of slow-moving and obsolete items.
- `/inventory/stockouts` (GET): Get stockout history and rates.
- `/inventory/stockouts/heatmap` (GET): Get data for a stockout heatmap.
- `/inventory/slow_movers/report` (GET): Download a CSV report of slow-moving and obsolete items.
- `/predict` (POST): Predict future inventory based on historical data. Accepts `store_id`, `product_id`, `granularity` (daily, monthly, quarterly, yearly), and `model_type` (linear_regression, random_forest, svm).
- `/metrics/all-metrics` (POST): Get all metrics for a specific store and product.

## Frontend Usage

Access the dashboard by navigating to `http://127.0.0.1:5000/` in your web browser.

### Demand Forecasting

In the "Demand Forecast" section:

1. Enter the **Store ID** and **Product ID** for which you want to generate a forecast.
2. Select the desired **Granularity** (Daily, Monthly, Quarterly, or Yearly) for the forecast.
3. Choose the **Model Type** (Linear Regression, Random Forest, or SVM) to be used for the prediction.
4. Click the "Generate Forecast" button to view the actual and predicted sales on the interactive chart.
