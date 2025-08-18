
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ForecastRequest(BaseModel):
    store_id: int
    product_id: int
    days: Optional[int] = 30  # Number of days to forecast

class MetricRequest(BaseModel):
    store_id: int
    product_id: int

class DataStatusResponse(BaseModel):
    is_loaded: bool
    record_count: int

class Inventory(BaseModel):
    item_id: str = Field(..., alias="_id")
    category: str
    ABC_class: Optional[str] = None
    stock_level: int
    avg_cost: float

class Sales(BaseModel):
    item_id: str
    date: datetime
    quantity: int
    revenue: float
    COGS: float

class Stockout(BaseModel):
    item_id: str
    date: datetime
    duration: Optional[float] = None
