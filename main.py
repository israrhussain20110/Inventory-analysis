import sys
import os
from fastapi import FastAPI
from routers import metrics, data, inventory
from database import create_indexes

app = FastAPI(
    title="Inventory Forecasting API",
    description="API for forecasting inventory levels and calculating metrics using the Retail Store Inventory Forecasting Dataset.",
    version="0.1.0"
)

@app.on_event("startup")
async def startup_event():
    create_indexes()

# Include routers for different tasks


app.include_router(data.router, prefix="/data", tags=["data"])
app.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Welcome to the Inventory Forecasting API. Use /docs for Swagger UI."}