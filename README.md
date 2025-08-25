# Inventory Forecasting Project

## Description

This project provides an advanced inventory forecasting and management system using FastAPI for the backend API and Flask for the frontend dashboard. It allows for uploading inventory and sales data, calculating various inventory metrics, and forecasting future inventory needs.

## Project Structure
```
inventory-forecasting/
├───api_descriptions.json       # Descriptions for API endpoints
├───config.py                   # Configuration settings
├───database.py                 # Database connection and functions
├───dependencies.py             # FastAPI dependencies
├───main.py                     # Main FastAPI application
├───models.py                   # Pydantic models for data validation
├───README.md                   # This file
├───requirements.txt            # Python dependencies
├───test_endpoints.py           # Tests for the API endpoints
├───data/                       # Sample data
├───notebooks/                  # Jupyter notebooks for experimentation
├───reporting/                  # Frontend dashboard application (Flask)
│   ├───app.py                  # Flask application
│   └───templates/
│       └───dashboard.html      # HTML template for the dashboard
├───routers/                    # API routers
│   ├───data.py                 # Router for data-related endpoints
│   ├───inventory.py            # Router for inventory-related endpoints
│   └───metrics.py              # Router for metrics-related endpoints
├───scripts/                    # Helper scripts
│   ├───load_csv_to_db.py       # Script to load CSV data into the database
│   └───...
└───services/                   # Business logic
    ├───calculations.py         # Functions for calculating inventory metrics
    ├───data_preprocessing.py   # Functions for data preprocessing
    └───...
```

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/inventory-forecasting.git
    cd inventory-forecasting
    ```

2.  **Create a virtual environment and activate it:**

    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your MongoDB URI:

    ```
    MONGO_URI="mongodb://localhost:27017/"
    ```

## How to Run

1.  **Start MongoDB:** Ensure your MongoDB instance is running.

2.  **Load Sample Data (Optional but Recommended):**
    Populate your MongoDB with sample data using the provided script:

    ```bash
    python scripts/load_csv_to_db.py data/retail_store_inventory.csv
    ```

3.  **Run the FastAPI Backend Application:**

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

    The API will be accessible at `http://127.0.0.1:8000`.

4.  **Run the Flask Frontend Application:**

    ```bash
    python reporting/app.py
    ```

    The frontend dashboard will be accessible at `http://127.0.0.1:5001/`.

## API Endpoints

-   `/docs`: Interactive API documentation (Swagger UI).
-   `/upload/{collection_name}` (POST): Upload CSV data to a specified MongoDB collection.
-   `/status` (GET): Check the data loading status.
-   `/inventory/all` (GET): Retrieves all inventory records from the database.
-   `/inventory/stockouts/all` (GET): Retrieves all stockout records from the database.
-   `/inventory/upload/inventory` (POST): Uploads inventory data from a CSV file to the database.
-   `/inventory/metrics` (GET): Get inventory metrics for a product.
-   `/inventory/slow_movers` (GET): Get a list of slow-moving and obsolete items.
-   `/inventory/stockouts` (GET): Get stockout history and rates.
-   `/inventory/stockouts/heatmap` (GET): Get data for a stockout heatmap.
-   `/inventory/slow_movers/report` (GET): Download a CSV report of slow-moving and obsolete items.
-   `/metrics/all-metrics` (POST): Get all metrics for a specific store and product.


## Contributing

Contributions are welcome! Please feel free to submit a pull request.