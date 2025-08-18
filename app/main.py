from fastapi import FastAPI
from app.routers import forecasting, metrics, data, inventory

app = FastAPI(
    title="Inventory Forecasting API",
    description="API for forecasting inventory levels and calculating metrics using the Retail Store Inventory Forecasting Dataset.",
    version="0.1.0"
)

# Include routers for different tasks
app.include_router(forecasting.router, prefix="/forecasting", tags=["forecasting"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(data.router, prefix="/data", tags=["data"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])

@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Welcome to the Inventory Forecasting API. Use /docs for Swagger UI."}