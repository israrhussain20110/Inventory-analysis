import os
import sys
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from database import insert_data, db # Added db import
from services import calculations
import pandas as pd
import io

router = APIRouter()

@router.get("/all")
async def get_all_inventory():
    """
    Retrieves all inventory records from the database.
    """
    inventory_data = list(db["inventory"].find({}, {"_id": 0})) # Exclude _id field
    return inventory_data

@router.get("/stockouts/all")
async def get_all_stockouts():
    """
    Retrieves all stockout records from the database.
    """
    stockouts_data = list(db["stockouts"].find({}, {"_id": 0})) # Exclude _id field
    return stockouts_data

@router.post("/upload/inventory")
async def upload_inventory(file: UploadFile = File(...)):
    """
    Uploads inventory data from a CSV file to the database.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        data = df.to_dict('records')
        insert_data(data, "inventory")
        return {"message": f"Successfully uploaded and inserted {len(data)} records from {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {e}")

@router.get("/metrics")
async def get_inventory_metrics(product_id: str = Query(None), period: str = Query('monthly')):
    """
    Computes and returns a dictionary of inventory metrics.
    """
    if product_id:
        turnover = calculations.calculate_turnover(product_id, period)
        stockout_rate = calculations.calculate_stockout_rate(product_id)
        days_of_supply = calculations.calculate_days_of_supply(product_id)
        carrying_cost = calculations.calculate_carrying_cost(product_id)
    else:
        # If no product_id, calculate for all and aggregate
        all_turnover = calculations.calculate_turnover(None, period)
        all_days_of_supply = calculations.calculate_days_of_supply(None)
        all_carrying_cost = calculations.calculate_carrying_cost(None)
        stockout_rate = calculations.calculate_stockout_rate(None)

        # Aggregate results
        if all_turnover:
            valid_turnover_ratios = [t.get("turnover_ratio", 0) for t in all_turnover if isinstance(t, dict)]
            turnover_value = sum(valid_turnover_ratios) / len(valid_turnover_ratios) if valid_turnover_ratios else 0
            turnover = {"turnover_ratio": turnover_value}
        else:
            turnover = {"turnover_ratio": 0}

        if all_days_of_supply:
            valid_dos_values = [d.get("days_of_supply", 0) for d in all_days_of_supply if isinstance(d, dict)]
            days_of_supply_value = sum(valid_dos_values) / len(valid_dos_values) if valid_dos_values else 0
            days_of_supply = {"days_of_supply": days_of_supply_value}
        else:
            days_of_supply = {"days_of_supply": 0}

        if all_carrying_cost:
            valid_cc_values = [c.get("carrying_cost", 0) for c in all_carrying_cost if isinstance(c, dict)]
            carrying_cost_value = sum(valid_cc_values) / len(valid_cc_values) if valid_cc_values else 0
            carrying_cost = {"carrying_cost": carrying_cost_value}
        else:
            carrying_cost = {"carrying_cost": 0}

    return {
        "turnover": turnover,
        "stockout_rate": stockout_rate,
        "days_of_supply": days_of_supply,
        "carrying_cost": carrying_cost
    }

@router.get("/slow_movers")
async def get_slow_movers():
    """
    Returns a list of slow-moving and obsolete items.
    """
    return calculations.detect_slow_obsolete_items()

@router.get("/stockouts")
async def get_stockouts(product_id: str = Query(None)):
    """
    Returns stockout history and rates.
    """
    return calculations.calculate_stockout_rate(product_id)

@router.get("/stockouts/heatmap")
async def get_stockouts_heatmap(product_id: str = Query(None)):
    """
    Returns data for a stockout heatmap.
    """
    return calculations.calculate_stockout_heatmap_data(product_id)

@router.get("/slow_movers/report")
async def get_slow_movers_report():
    """
    Generates a CSV report of slow-moving and obsolete items.
    """
    data = calculations.detect_slow_obsolete_items()
    if "error" in data:
        # If there's an error indicating no data, return an empty CSV
        if data["error"] == "No inventory data found.":
            df = pd.DataFrame(columns=['Product ID', 'status'])
            stream = io.StringIO()
            df.to_csv(stream, index=False)
            response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
            response.headers["Content-Disposition"] = "attachment; filename=slow_movers_report.csv"
            return response
        else:
            # For other errors, raise HTTPException
            raise HTTPException(status_code=500, detail=data["error"])

    slow_movers_df = pd.DataFrame(data['slow_movers'], columns=['Product ID'])
    slow_movers_df['status'] = 'slow-moving'

    obsolete_items_df = pd.DataFrame(data['obsolete_items'], columns=['Product ID'])
    obsolete_items_df['status'] = 'obsolete'

    df = pd.concat([slow_movers_df, obsolete_items_df])

    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=slow_movers_report.csv"
    return response