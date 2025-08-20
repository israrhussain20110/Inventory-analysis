from pydantic import BaseModel, Field
from typing import Optional

class InventoryItem(BaseModel):
    Date: str
    ProductID: str = Field(..., alias='Product ID')
    InventoryLevel: int = Field(..., alias='Inventory Level')

    class Config:
        populate_by_name = True

class SalesRecord(BaseModel):
    Date: str
    ProductID: str = Field(..., alias='Product ID')
    UnitsSold: int = Field(..., alias='Units Sold')
    Price: float

    class Config:
        populate_by_name = True

class MetricRequest(BaseModel):
    store_id: str = Field(..., alias='Store ID')
    product_id: str = Field(..., alias='Product ID')

class DataStatusResponse(BaseModel):
    is_loaded: bool
    record_count: int

class ForecastRequest(BaseModel):
    store_id: str = Field(..., alias='Store ID')
    product_id: str = Field(..., alias='Product ID')