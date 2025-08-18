
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from app.database import insert_data
from app.services import calculations
import pandas as pd
import io

router = APIRouter()

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
    turnover = calculations.calculate_turnover(product_id, period)
    stockout_rate = calculations.calculate_stockout_rate(product_id)
    days_of_supply = calculations.calculate_days_of_supply(product_id)
    carrying_cost = calculations.calculate_carrying_cost(product_id)

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
